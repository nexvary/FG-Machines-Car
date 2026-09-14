from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
native = root / 'native'
modern = native / 'src' / 'app' / 'modern'
cmake = native / 'CMakeLists.txt'

for p in (modern / 'ModernHost.hpp', modern / 'ModernHost.cpp', modern / 'main.cpp', cmake):
    if not p.exists():
        raise SystemExit(f'UBUNTU24_PORT_MISSING {p}')

hpp = r'''#pragma once
#include <atomic>
#include <cstdint>
#include <filesystem>
#include <string>
#include <string_view>
#include <thread>

namespace fg::modern {
class ModernHost final {
public:
    ModernHost();
    ~ModernHost();
    int run();
    int self_test();
    int qa_server(std::uint16_t fixed_port=43890);
private:
    using socket_native = int;
    static constexpr socket_native invalid_socket = -1;

    std::filesystem::path exe_dir_;
    std::filesystem::path ui_dir_;
    std::atomic_bool stop_{false};
    socket_native listen_socket_{invalid_socket};
    std::thread server_thread_;
    std::uint16_t port_{};
    std::atomic_int ui_selftest_result_{-1};

    bool initialize_network();
    bool start_server(std::uint16_t preferred_port=0);
    void stop_server();
    void server_loop();
    void handle_client(socket_native client);
    std::string build_response(std::string_view target);
    std::string api_status() const;
    std::string api_navigation(std::string_view lang) const;
    std::string api_page(std::string_view target) const;
    std::string serve_asset(std::string_view path) const;
    std::filesystem::path find_browser() const;
    int launch_browser_app();
    bool launch_headless_ui_selftest();
    std::string local_probe(std::string_view path) const;
};
}
'''

cpp = r'''#include "ModernHost.hpp"
#include "fg/core/ModuleRegistry.hpp"
#include "fg/core/BuildIdentity.hpp"
#include "fg/ui/MultiLanguageCatalog.hpp"
#include "fg/ui/NativePageModel.hpp"

#include <algorithm>
#include <array>
#include <arpa/inet.h>
#include <cerrno>
#include <chrono>
#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <map>
#include <netinet/in.h>
#include <sstream>
#include <string>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>
#include <vector>

namespace fg::modern { namespace fs=std::filesystem;
namespace {
std::string json_escape(std::string_view s){std::string o;o.reserve(s.size()+16);for(unsigned char c:s){switch(c){case '"':o+="\\\"";break;case '\\':o+="\\\\";break;case '\b':o+="\\b";break;case '\f':o+="\\f";break;case '\n':o+="\\n";break;case '\r':o+="\\r";break;case '\t':o+="\\t";break;default:if(c<0x20){char b[7]{};std::snprintf(b,sizeof(b),"\\u%04x",c);o+=b;}else o.push_back(static_cast<char>(c));}}return o;}
std::string url_decode(std::string_view s){std::string o;o.reserve(s.size());auto hex=[](char c)->int{if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;if(c>='A'&&c<='F')return c-'A'+10;return -1;};for(size_t i=0;i<s.size();++i){if(s[i]=='%'&&i+2<s.size()){int a=hex(s[i+1]),b=hex(s[i+2]);if(a>=0&&b>=0){o.push_back(static_cast<char>((a<<4)|b));i+=2;continue;}}o.push_back(s[i]=='+'?' ':s[i]);}return o;}
std::string query_value(std::string_view target,std::string_view key){const auto q=target.find('?');if(q==std::string_view::npos)return{};std::string_view rest=target.substr(q+1);while(!rest.empty()){const auto amp=rest.find('&');auto part=rest.substr(0,amp);const auto eq=part.find('=');if(eq!=std::string_view::npos&&part.substr(0,eq)==key)return url_decode(part.substr(eq+1));if(amp==std::string_view::npos)break;rest=rest.substr(amp+1);}return{};}
std::string path_only(std::string_view target){const auto q=target.find('?');return std::string(target.substr(0,q));}
std::string content_type(std::string_view p){if(p.ends_with(".html"))return"text/html; charset=utf-8";if(p.ends_with(".css"))return"text/css; charset=utf-8";if(p.ends_with(".js"))return"application/javascript; charset=utf-8";if(p.ends_with(".svg"))return"image/svg+xml; charset=utf-8";if(p.ends_with(".json"))return"application/json; charset=utf-8";return"application/octet-stream";}
std::string http(int code,std::string_view type,const std::string& body){std::ostringstream o;o<<"HTTP/1.1 "<<code<<(code==200?" OK":" Not Found")<<"\r\nContent-Type: "<<type<<"\r\nContent-Length: "<<body.size()<<"\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nConnection: close\r\n\r\n"<<body;return o.str();}
bool send_all(int s,const std::string& data){size_t sent=0;while(sent<data.size()){const auto n=::send(s,data.data()+sent,data.size()-sent,MSG_NOSIGNAL);if(n<=0)return false;sent+=static_cast<size_t>(n);}return true;}
fs::path exe_directory(){std::array<char,4096>b{};const auto n=::readlink("/proc/self/exe",b.data(),b.size()-1);if(n>0)return fs::path(std::string(b.data(),static_cast<size_t>(n))).parent_path();return fs::current_path();}
std::string envs(const char* n){const char* v=std::getenv(n);return v?std::string(v):std::string{};}
std::string section_icon(std::string_view s){if(s=="diagnostics")return"pulse";if(s=="cars")return"car";if(s=="motorcycles")return"moto";if(s=="yamaha")return"bike";if(s=="lancer")return"gauge";if(s=="keys")return"key";if(s=="obdvci")return"plug";if(s=="maintenance")return"wrench";if(s=="road")return"road";if(s=="garage")return"garage";if(s=="network")return"network";if(s=="reports")return"report";if(s=="settings")return"settings";if(s=="about")return"info";return"home";}
fs::path cache_root(){auto x=envs("XDG_CACHE_HOME");if(!x.empty())return fs::path(x)/"fg-machines-car";auto h=envs("HOME");return h.empty()?fs::temp_directory_path()/"fg-machines-car":fs::path(h)/".cache"/"fg-machines-car";}
fs::path path_lookup(const std::string& name){auto p=envs("PATH");std::stringstream ss(p);std::string d;while(std::getline(ss,d,':')){if(d.empty())continue;fs::path c=fs::path(d)/name;std::error_code ec;if(fs::exists(c,ec)&&::access(c.c_str(),X_OK)==0)return c;}return{};}
pid_t spawn_process(const fs::path& exe,const std::vector<std::string>& args){pid_t pid=::fork();if(pid<0)return-1;if(pid==0){std::vector<std::string> storage;storage.reserve(args.size()+1);storage.push_back(exe.string());storage.insert(storage.end(),args.begin(),args.end());std::vector<char*> argv;argv.reserve(storage.size()+1);for(auto&v:storage)argv.push_back(v.data());argv.push_back(nullptr);::execv(exe.c_str(),argv.data());::_exit(127);}return pid;}
}

ModernHost::ModernHost():exe_dir_(exe_directory()),ui_dir_(exe_dir_/"ui"){}
ModernHost::~ModernHost(){stop_server();}
bool ModernHost::initialize_network(){return true;}
bool ModernHost::start_server(std::uint16_t preferred_port){if(!initialize_network())return false;listen_socket_=::socket(AF_INET,SOCK_STREAM,0);if(listen_socket_==invalid_socket)return false;int one=1;::setsockopt(listen_socket_,SOL_SOCKET,SO_REUSEADDR,&one,sizeof(one));sockaddr_in a{};a.sin_family=AF_INET;a.sin_addr.s_addr=htonl(INADDR_LOOPBACK);a.sin_port=htons(preferred_port);if(::bind(listen_socket_,reinterpret_cast<sockaddr*>(&a),sizeof(a))!=0){::close(listen_socket_);listen_socket_=invalid_socket;return false;}if(::listen(listen_socket_,8)!=0){::close(listen_socket_);listen_socket_=invalid_socket;return false;}socklen_t len=sizeof(a);if(::getsockname(listen_socket_,reinterpret_cast<sockaddr*>(&a),&len)!=0){::close(listen_socket_);listen_socket_=invalid_socket;return false;}port_=ntohs(a.sin_port);stop_=false;server_thread_=std::thread(&ModernHost::server_loop,this);return true;}
void ModernHost::stop_server(){stop_=true;if(listen_socket_!=invalid_socket){::shutdown(listen_socket_,SHUT_RDWR);::close(listen_socket_);listen_socket_=invalid_socket;}if(server_thread_.joinable())server_thread_.join();}
void ModernHost::server_loop(){while(!stop_){sockaddr_in c{};socklen_t n=sizeof(c);int client=::accept(listen_socket_,reinterpret_cast<sockaddr*>(&c),&n);if(client==invalid_socket){if(stop_)break;if(errno==EINTR)continue;std::this_thread::sleep_for(std::chrono::milliseconds(20));continue;}handle_client(client);::close(client);}}
void ModernHost::handle_client(socket_native client){std::array<char,16384>b{};const auto n=::recv(client,b.data(),b.size()-1,0);if(n<=0)return;std::string_view req(b.data(),static_cast<size_t>(n));const auto e=req.find("\r\n");if(e==std::string_view::npos)return;const auto line=req.substr(0,e);const auto sp1=line.find(' '),sp2=sp1==std::string_view::npos?sp1:line.find(' ',sp1+1);if(sp1==std::string_view::npos||sp2==std::string_view::npos)return;if(line.substr(0,sp1)!="GET")return;send_all(client,build_response(line.substr(sp1+1,sp2-sp1-1)));}
std::string ModernHost::build_response(std::string_view target){const auto p=path_only(target);if(p=="/api/status"||p=="/api/ping")return http(200,"application/json; charset=utf-8",api_status());if(p=="/api/ui-selftest"){const auto result=query_value(target,"result"),count=query_value(target,"count");if(result=="pass"){try{ui_selftest_result_.store(std::stoi(count));}catch(...){ui_selftest_result_.store(0);}}else ui_selftest_result_.store(0);return http(200,"application/json; charset=utf-8","{\"ok\":true}");}if(p=="/api/navigation"){auto l=query_value(target,"lang");return http(200,"application/json; charset=utf-8",api_navigation(l.empty()?"ar":l));}if(p=="/api/page")return http(200,"application/json; charset=utf-8",api_page(target));const auto body=serve_asset(p);if(body.empty()&&p!="/app.js"&&p!="/app.css")return http(404,"text/plain; charset=utf-8","Not found");return http(200,content_type(p=="/"?"index.html":p),body);}
std::string ModernHost::api_status()const{std::ostringstream o;o<<"{\"product\":\"FG Machines Car\",\"stage\":"<<fg::core::BuildIdentity::stage()<<",\"version\":\""<<fg::core::BuildIdentity::version()<<"\",\"readOnly\":"<<(fg::core::BuildIdentity::read_only()?"true":"false")<<",\"modules\":"<<fg::core::ModuleRegistry::module_count()<<",\"sections\":"<<fg::core::ModuleRegistry::section_count()<<",\"languages\":"<<fg::ui::MultiLanguageCatalog::languages().size()<<",\"core\":\"C++20 Native Ubuntu\",\"state\":\"جاهز\"}";return o.str();}
std::string ModernHost::api_navigation(std::string_view lang)const{std::vector<std::string> order;std::map<std::string,std::vector<const fg::core::ModuleDescriptor*>> groups;for(const auto&m:fg::core::ModuleRegistry::all()){if(!groups.contains(m.section))order.push_back(m.section);groups[m.section].push_back(&m);}std::ostringstream o;o<<'[';bool firsts=true;for(const auto&s:order){const auto&g=groups[s];if(g.empty())continue;const auto sl=fg::ui::MultiLanguageCatalog::navigation(g.front()->route_key,lang);if(!firsts)o<<',';firsts=false;o<<"{\"id\":\""<<json_escape(s)<<"\",\"title\":\""<<json_escape(sl.section)<<"\",\"icon\":\""<<section_icon(s)<<"\",\"count\":"<<g.size()<<",\"modules\":[";bool firstm=true;for(const auto*m:g){const auto l=fg::ui::MultiLanguageCatalog::navigation(m->route_key,lang);if(!firstm)o<<',';firstm=false;o<<"{\"route\":\""<<json_escape(m->route_key)<<"\",\"title\":\""<<json_escape(l.title)<<"\",\"safety\":\""<<json_escape(l.safety)<<"\"}";}o<<"]}";}o<<']';return o.str();}
std::string ModernHost::api_page(std::string_view target)const{const auto route=query_value(target,"route");auto lang=query_value(target,"lang");if(lang.empty())lang="ar";if(route.empty())return"{\"error\":\"missing route\"}";try{const auto p=fg::ui::NativePageFactory::build(route);const auto l=fg::ui::MultiLanguageCatalog::navigation(route,lang);std::ostringstream o;o<<"{\"route\":\""<<json_escape(route)<<"\",\"section\":\""<<json_escape(p.section)<<"\",\"title\":\""<<json_escape(l.title)<<"\",\"safety\":\""<<json_escape(l.safety.empty()?p.safety_note:l.safety)<<"\",\"fields\":[";for(size_t i=0;i<p.fields.size();++i){if(i)o<<',';o<<"{\"label\":\""<<json_escape(p.fields[i].label)<<"\",\"value\":\""<<json_escape(p.fields[i].value)<<"\"}";}o<<"],\"actions\":[";for(size_t i=0;i<p.actions.size();++i){if(i)o<<',';o<<'\"'<<json_escape(p.actions[i])<<'\"';}o<<"]}";return o.str();}catch(...){return"{\"error\":\"unknown route\"}";}}
std::string ModernHost::serve_asset(std::string_view path)const{std::string f;if(path=="/"||path=="/index.html")f="index.html";else{f=std::string(path);while(!f.empty()&&f.front()=='/')f.erase(f.begin());}if(f.empty()||f.find("..")!=std::string::npos||f.find('\\')!=std::string::npos||f.find(':')!=std::string::npos)return{};const auto ext=fs::path(f).extension().string();if(ext!=".html"&&ext!=".css"&&ext!=".js"&&ext!=".svg"&&ext!=".json")return{};std::ifstream in(ui_dir_/fs::path(f),std::ios::binary);if(!in)return{};return std::string(std::istreambuf_iterator<char>(in),std::istreambuf_iterator<char>());}
fs::path ModernHost::find_browser()const{const auto requested=envs("FG_BROWSER");if(!requested.empty()){fs::path p=requested;std::error_code ec;if(fs::exists(p,ec)&&::access(p.c_str(),X_OK)==0)return p;}const std::array<const char*,4> names={"google-chrome-stable","google-chrome","chromium","chromium-browser"};for(const auto*n:names){auto p=path_lookup(n);if(!p.empty())return p;}const std::array<const char*,3> direct={"/usr/bin/google-chrome-stable","/usr/bin/google-chrome","/snap/bin/chromium"};for(const auto*n:direct){fs::path p=n;std::error_code ec;if(fs::exists(p,ec)&&::access(p.c_str(),X_OK)==0)return p;}return{};}
int ModernHost::launch_browser_app(){const auto browser=find_browser();if(browser.empty()){std::cerr<<"FG Machines Car: Chrome/Chromium browser was not found. Install google-chrome-stable or chromium, or set FG_BROWSER.\n";return 21;}const fs::path profile=cache_root()/("BrowserProfile-140000-"+std::to_string(::getpid()));std::error_code ec;fs::remove_all(profile,ec);fs::create_directories(profile,ec);const std::string url="http://127.0.0.1:"+std::to_string(port_)+"/";std::vector<std::string> args={"--app="+url,"--start-maximized","--no-first-run","--no-default-browser-check","--disable-background-mode","--disable-extensions","--user-data-dir="+profile.string()};const pid_t pid=spawn_process(browser,args);if(pid<0)return 22;int status=0;while(::waitpid(pid,&status,0)<0&&errno==EINTR){}fs::remove_all(profile,ec);return 0;}
bool ModernHost::launch_headless_ui_selftest(){const auto browser=find_browser();if(browser.empty())return false;ui_selftest_result_.store(-1);const fs::path profile=cache_root()/("SelfTestProfile-140000-"+std::to_string(::getpid()));std::error_code ec;fs::remove_all(profile,ec);fs::create_directories(profile,ec);const std::string url="http://127.0.0.1:"+std::to_string(port_)+"/navigation-selftest.html?selftest=1";std::vector<std::string> args={"--headless=new","--disable-gpu","--no-first-run","--no-default-browser-check","--disable-background-mode","--disable-extensions","--user-data-dir="+profile.string(),url};if(::geteuid()==0)args.insert(args.begin(),"--no-sandbox");const pid_t pid=spawn_process(browser,args);if(pid<0)return false;const auto deadline=std::chrono::steady_clock::now()+std::chrono::seconds(15);int status=0;bool exited=false;while(std::chrono::steady_clock::now()<deadline){if(ui_selftest_result_.load()>=0)break;const auto r=::waitpid(pid,&status,WNOHANG);if(r==pid){exited=true;break;}std::this_thread::sleep_for(std::chrono::milliseconds(50));}if(!exited){::kill(pid,SIGTERM);for(int i=0;i<20;++i){if(::waitpid(pid,&status,WNOHANG)==pid){exited=true;break;}std::this_thread::sleep_for(std::chrono::milliseconds(50));}if(!exited){::kill(pid,SIGKILL);::waitpid(pid,&status,0);}}const int result=ui_selftest_result_.load();fs::remove_all(profile,ec);return result>=10;}
std::string ModernHost::local_probe(std::string_view path)const{int s=::socket(AF_INET,SOCK_STREAM,0);if(s<0)return{};sockaddr_in a{};a.sin_family=AF_INET;a.sin_port=htons(port_);::inet_pton(AF_INET,"127.0.0.1",&a.sin_addr);if(::connect(s,reinterpret_cast<sockaddr*>(&a),sizeof(a))!=0){::close(s);return{};}const std::string req="GET "+std::string(path)+" HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n";send_all(s,req);std::string out;std::array<char,8192>b{};for(;;){const auto n=::recv(s,b.data(),b.size(),0);if(n<=0)break;out.append(b.data(),static_cast<size_t>(n));if(out.size()>2*1024*1024)break;}::close(s);return out;}
int ModernHost::self_test(){if(!initialize_network())return 80;const std::vector<std::string> required={"index.html","app.css","common.js","module.js","navigation-manifest.json","navigation-selftest.html","navigation-selftest.js","fg-icon.svg"};for(const auto&f:required)if(!fs::exists(ui_dir_/f))return 81;if(fs::exists(ui_dir_/"app.js")||fs::exists(ui_dir_/"router.js"))return 82;if(fg::core::ModuleRegistry::module_count()!=159||fg::core::ModuleRegistry::section_count()<15)return 83;if(find_browser().empty())return 84;const auto index=serve_asset("/index.html");if(index.find("data-static-page=\"home\"")==std::string::npos||index.find("/sections/diagnostics.html")==std::string::npos||index.find("/sections/reports.html")==std::string::npos)return 85;const std::vector<std::string> section_pages={"diagnostics","cars","motorcycles","yamaha","lancer","keys","obdvci","maintenance","road","garage","network","reports","settings","about"};for(const auto&s:section_pages){const auto p=serve_asset("/sections/"+s+".html");if(p.find("data-static-page=\"section:"+s+"\"")==std::string::npos)return 86;}if(!start_server())return 87;std::this_thread::sleep_for(std::chrono::milliseconds(80));const auto status=local_probe("/api/status?lang=ar");if(status.find("200 OK")==std::string::npos||status.find("140000")==std::string::npos){stop_server();return 88;}for(const auto&s:section_pages){const auto p=local_probe("/sections/"+s+".html");if(p.find("200 OK")==std::string::npos||p.find("data-static-page=\"section:"+s+"\"")==std::string::npos){stop_server();return 89;}}const auto manifest=local_probe("/navigation-manifest.json");if(manifest.find("200 OK")==std::string::npos||manifest.find("\"stage\": 140000")==std::string::npos){stop_server();return 90;}const std::vector<std::string> api_probes={"diagnostics%3A%3AFull%20Vehicle%20Scan","cars%3A%3ACar%20Baselines","lancer%3A%3AShark%202013%20Transmission%20Center","keys%3A%3AKey%20%26%20Remote%20Service%20Center","obdvci%3A%3AMulti-VCI%20Manager","reports%3A%3ADiagnostic%20Reports"};for(const auto&r:api_probes){const auto p=local_probe("/api/page?route="+r+"&lang=ar");if(p.find("200 OK")==std::string::npos||p.find("\"route\"")==std::string::npos||p.find("\"section\"")==std::string::npos){stop_server();return 91;}}if(!launch_headless_ui_selftest()){stop_server();return 92;}stop_server();return 0;}
int ModernHost::qa_server(std::uint16_t fixed_port){if(!start_server(fixed_port))return 93;const auto ready=envs("FG_QA_READY_FILE");if(!ready.empty()){std::ofstream o(fs::path(ready),std::ios::binary);if(o)o<<"http://127.0.0.1:"<<port_<<"/\n";}while(true)std::this_thread::sleep_for(std::chrono::seconds(1));}
int ModernHost::run(){if(!start_server()){std::cerr<<"FG Machines Car: local UI service could not start.\n";return 10;}const int rc=launch_browser_app();stop_server();return rc;}
}
'''

main = r'''#include "ModernHost.hpp"
#include <string_view>
int main(int argc,char**argv){
    fg::modern::ModernHost host;
    for(int i=1;i<argc;++i){
        const std::string_view a=argv[i];
        if(a=="--self-test")return host.self_test();
        if(a=="--qa-server")return host.qa_server(43890);
    }
    return host.run();
}
'''

(modern / 'ModernHost.hpp').write_text(hpp, encoding='utf-8')
(modern / 'ModernHost.cpp').write_text(cpp, encoding='utf-8')
(modern / 'main.cpp').write_text(main, encoding='utf-8')

text = cmake.read_text(encoding='utf-8')
marker = '# FG-UBUNTU24-MODERN-HOST-V1'
if marker not in text:
    text += r'''

# FG-UBUNTU24-MODERN-HOST-V1
if(FG_BUILD_MODERN_UI AND UNIX AND NOT APPLE)
  add_executable(FG-Machines-Car-Modern
    src/app/modern/main.cpp
    src/app/modern/ModernHost.cpp
    src/app/modern/ModernHost.hpp)
  target_include_directories(FG-Machines-Car-Modern PRIVATE src/app/modern)
  target_link_libraries(FG-Machines-Car-Modern PRIVATE fg_native_core Threads::Threads)
  target_compile_options(FG-Machines-Car-Modern PRIVATE -Wall -Wextra -Wpedantic -Werror)
  set_target_properties(FG-Machines-Car-Modern PROPERTIES OUTPUT_NAME "FG-Machines-Car")
  add_custom_command(TARGET FG-Machines-Car-Modern POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      ${CMAKE_CURRENT_SOURCE_DIR}/ui-modern
      $<TARGET_FILE_DIR:FG-Machines-Car-Modern>/ui)
endif()
'''
    cmake.write_text(text, encoding='utf-8')

print('UBUNTU24_PORT_APPLIED version=V1 host=posix browser=chrome-chromium modern_ui=true routes_preserved=true')
