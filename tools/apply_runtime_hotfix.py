from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
header = root / 'native/src/app/modern/ModernHost.hpp'
cpp = root / 'native/src/app/modern/ModernHost.cpp'
js = root / 'native/ui-modern/common.js'
qa = root / 'qa/visual/ui.spec.cjs'

for p in (header, cpp, js, qa):
    if not p.exists():
        raise SystemExit(f'HOTFIX_MISSING_FILE {p}')

s = header.read_text(encoding='utf-8')
old = '    std::atomic_int ui_selftest_result_{-1};\n\n    bool initialize_network();'
new = '    std::atomic_int ui_selftest_result_{-1};\n    std::atomic_llong last_ui_ping_ms_{0};\n\n    bool initialize_network();'
if 'last_ui_ping_ms_' not in s:
    if old not in s:
        raise SystemExit('HOTFIX_HEADER_ANCHOR_NOT_FOUND')
    s = s.replace(old, new, 1)
header.write_text(s, encoding='utf-8')

s = cpp.read_text(encoding='utf-8')
anchor = 'std::wstring envw(const wchar_t* n){const wchar_t* v=_wgetenv(n);return v?std::wstring(v):std::wstring{};}\n'
if 'long long steady_ms()' not in s:
    if anchor not in s:
        raise SystemExit('HOTFIX_CPP_HELPER_ANCHOR_NOT_FOUND')
    s = s.replace(anchor, anchor + 'long long steady_ms(){return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}\n', 1)

old_ping = 'std::string ModernHost::build_response(std::string_view target){const auto p=path_only(target);if(p=="/api/status"||p=="/api/ping")return http(200,"application/json; charset=utf-8",api_status());'
new_ping = 'std::string ModernHost::build_response(std::string_view target){const auto p=path_only(target);if(p=="/api/ping"){last_ui_ping_ms_.store(steady_ms());return http(200,"application/json; charset=utf-8",api_status());}if(p=="/api/status")return http(200,"application/json; charset=utf-8",api_status());'
if 'last_ui_ping_ms_.store(steady_ms())' not in s:
    if old_ping not in s:
        raise SystemExit('HOTFIX_CPP_PING_ANCHOR_NOT_FOUND')
    s = s.replace(old_ping, new_ping, 1)

start = s.find('int ModernHost::launch_edge_app(){')
end = s.find('\nbool ModernHost::launch_headless_ui_selftest()', start)
if start < 0 or end < 0:
    raise SystemExit('HOTFIX_CPP_LAUNCH_FUNCTION_NOT_FOUND')
launch = r'''int ModernHost::launch_edge_app(){
    const auto edge=find_edge();
    if(edge.empty()){
        MessageBoxW(nullptr,L"Microsoft Edge was not found. FG Machines Car uses the installed Edge engine only as its modern local interface; no Internet connection is required during normal use.",L"FG Machines Car",MB_OK|MB_ICONERROR);
        return 21;
    }
    const auto la=envw(L"LOCALAPPDATA");
    const fs::path profile=(la.empty()?exe_dir_:fs::path(la)/L"FGMachinesCar")/(L"EdgeProfile-140000-RUNTIME-"+std::to_wstring(GetCurrentProcessId()));
    std::error_code ec;
    fs::remove_all(profile,ec);
    fs::create_directories(profile,ec);
    const std::wstring url=L"http://127.0.0.1:"+std::to_wstring(port_)+L"/";
    const bool headless=!envw(L"FG_UI_HEADLESS").empty();
    std::wstring cmd;
    if(headless){
        cmd=L"\""+edge.wstring()+L"\" --headless=new --disable-gpu --no-first-run --no-default-browser-check --disable-background-mode --disable-extensions --user-data-dir=\""+profile.wstring()+L"\" \""+url+L"\"";
    }else{
        cmd=L"\""+edge.wstring()+L"\" --app="+url+L" --start-maximized --no-first-run --no-default-browser-check --disable-background-mode --user-data-dir=\""+profile.wstring()+L"\"";
    }
    STARTUPINFOW si{};si.cb=sizeof(si);
    if(headless){si.dwFlags=STARTF_USESHOWWINDOW;si.wShowWindow=SW_HIDE;}
    PROCESS_INFORMATION pi{};
    const DWORD flags=CREATE_UNICODE_ENVIRONMENT|(headless?CREATE_NO_WINDOW:0);
    if(!CreateProcessW(nullptr,cmd.data(),nullptr,nullptr,FALSE,flags,nullptr,nullptr,&si,&pi)){
        MessageBoxW(nullptr,L"Unable to start the modern FG Machines Car interface.",L"FG Machines Car",MB_OK|MB_ICONERROR);
        return 22;
    }
    WaitForInputIdle(pi.hProcess,10000);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return 0;
}'''
s = s[:start] + launch + s[end:]

old_run = 'int ModernHost::run(){if(!start_server()){MessageBoxW(nullptr,L"The local FG Machines Car service could not start.",L"FG Machines Car",MB_OK|MB_ICONERROR);return 10;}const int rc=launch_edge_app();stop_server();return rc;}'
run = r'''int ModernHost::run(){
    std::uint16_t preferred=0;
    const auto requestedPort=envw(L"FG_UI_PORT");
    if(!requestedPort.empty()){
        try{const int p=std::stoi(requestedPort);if(p>0&&p<65536)preferred=static_cast<std::uint16_t>(p);}catch(...){}
    }
    if(!start_server(preferred)){
        MessageBoxW(nullptr,L"The local FG Machines Car service could not start.",L"FG Machines Car",MB_OK|MB_ICONERROR);
        return 10;
    }
    last_ui_ping_ms_.store(0);
    const long long launched=steady_ms();
    long long maxRuntimeMs=0;
    const auto maxRuntime=envw(L"FG_UI_MAX_RUNTIME_SECONDS");
    if(!maxRuntime.empty()){
        try{const long long seconds=std::stoll(maxRuntime);if(seconds>0)maxRuntimeMs=seconds*1000;}catch(...){}
    }
    const int rc=launch_edge_app();
    if(rc!=0){stop_server();return rc;}

    const long long firstPingDeadline=launched+25000;
    while(last_ui_ping_ms_.load()==0 && steady_ms()<firstPingDeadline){
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    if(last_ui_ping_ms_.load()==0){
        stop_server();
        MessageBoxW(nullptr,L"The FG Machines Car interface started, but it did not connect to the local service.",L"FG Machines Car",MB_OK|MB_ICONERROR);
        return 23;
    }

    while(true){
        const long long now=steady_ms();
        const long long last=last_ui_ping_ms_.load();
        if(last>0 && now-last>10000)break;
        if(maxRuntimeMs>0 && now-launched>=maxRuntimeMs)break;
        std::this_thread::sleep_for(std::chrono::milliseconds(250));
    }
    stop_server();
    return 0;
}'''
if old_run not in s:
    raise SystemExit('HOTFIX_CPP_RUN_ANCHOR_NOT_FOUND')
s = s.replace(old_run, run, 1)
cpp.write_text(s, encoding='utf-8')

s = js.read_text(encoding='utf-8')
needle = "  window.fgManifest=manifest;\n})();\n"
insert = "  const fgHeartbeat=()=>fetch('/api/ping',{cache:'no-store',keepalive:true}).catch(()=>{});\n  fgHeartbeat();\n  setInterval(fgHeartbeat,2000);\n  window.fgManifest=manifest;\n})();\n"
if 'const fgHeartbeat=' not in s:
    if needle not in s:
        raise SystemExit('HOTFIX_JS_ANCHOR_NOT_FOUND')
    s = s.replace(needle, insert, 1)
else:
    s = s.replace("fetch('/api/ping',{cache:'no-store'})", "fetch('/api/ping',{cache:'no-store',keepalive:true})")
js.write_text(s, encoding='utf-8')

q = qa.read_text(encoding='utf-8')
old_watch = "function watchErrors(page){const errs=[];page.on('console',m=>{if(m.type()==='error')errs.push(m.text())});page.on('pageerror',e=>errs.push(String(e)));page.on('requestfailed',r=>errs.push('REQUEST '+r.url()+' '+(r.failure()?.errorText||'')));return errs}"
new_watch = "function watchErrors(page){const errs=[];page.on('console',m=>{if(m.type()==='error')errs.push(m.text())});page.on('pageerror',e=>errs.push(String(e)));page.on('requestfailed',r=>{const u=r.url();const e=r.failure()?.errorText||'';if(u.endsWith('/api/ping')&&e==='net::ERR_ABORTED')return;errs.push('REQUEST '+u+' '+e)});return errs}"
if old_watch in q:
    q = q.replace(old_watch, new_watch, 1)
elif new_watch not in q:
    raise SystemExit('HOTFIX_QA_WATCH_ANCHOR_NOT_FOUND')
qa.write_text(q, encoding='utf-8')

print('RUNTIME_HOTFIX_APPLIED release=Stage140000-RUNTIME-HOTFIX-R3 heartbeat=true keepalive=true navAbortFilter=ping-only edgeLauncherDetached=true')
