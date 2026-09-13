#!/usr/bin/env python3
import argparse, base64, hashlib, pathlib, tarfile, sys

EXPECTED = {
'000': (8000,'1d12d2841b813f420e642e4ebf04e08f45e37881'),
'001': (8000,'64ade0d64a8284a425851fafd719ee7cba2d924c'),
'002': (8000,'73b05ef1f1287c731ca68fc412593535291dbab8'),
'003': (8000,'a58ccf323f6b5ca69ba1da4489bb776a02bbdb7b'),
'004': (8000,'7d76ec8134c9cb96e656acf9f25593af4e7f9be9'),
'005': (8000,'d69b34f16a6a595b5a0ae62d66058d8c0466e6ea'),
'006': (8000,'b1a9b40e936d816d11a6ba35da36f2e1c840ab33'),
'007': (8000,'1a5bae226763e2cafe61ba59024d4263e129b759'),
'008': (8000,'b41a6de62a0ed21b2134a23049e9e6ca76afbc0a'),
'009': (8000,'41ef6e922fd9e64f6c1f88352f17fb931f54162f'),
'010': (8000,'fba0e866894166adac23b33141bf8efe6f02ff24'),
'011': (8000,'9742a316719e6db9764a5bc321f265a75e7186db'),
'012': (8000,'993eb2cac6a805ff534c0bcb587f2a6b0d3d5bef'),
'013': (8000,'8ed7586fcc93989ac3df9234d1cad455b0c64bf6'),
'014': (8000,'5f986a0f1783a6d30769183888e95e6eaccf8b91'),
'015': (8000,'fa36dc61c6e6fe35575306bc0083172b4385bd0a'),
'016': (8000,'c2f7c5a7208bb37aec078b6cbd008694e5a2dc13'),
'017': (8000,'606507b863dace3d7dd983677e450e232f1c5bf8'),
'018': (8000,'934ef5f63dc00b70dd747a236b63cf027ad28c04'),
'019': (8000,'dcc981f30aa7ac7df2811465001e32e048311802'),
'020': (8000,'64a779b9c8b2d7db46b9dd0789d9b85371ba5dc4'),
'021': (8000,'cb772dd6776bf5d743bbefbb115618490403852c'),
'022': (8000,'60c2fb04ef078927101a612ff13187440eb047b8'),
'023': (8000,'f62d44524e4a544aa49f6dfcb524d7357f07bc0e'),
'024': (8000,'5393acaac98254cd946862730d79fd89bb5ed2d4'),
'025': (6288,'c9950438283700b84b466268d7bcccf29d91ff83'),
}
ARCHIVE_SIZE = 154716
ENCODED_SIZE = 206288
ARCHIVE_SHA256 = '11448329307471388b7d49545900c8472055db18f6e4ed495f328108252898cc'
B64_ALPHABET = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='

BLOCK_HASHES_017 = [
    '4342a875a9a13f508845b47703ec2ee5ea079f3b9c5b6505fe00e6ef7b740ce6',
    '576b9cdbed69b579ca959e44c8fd56b8da1ee675ebe3c93280f7d7d05294ca7a',
    '1fbe9b0e19cc6648b42aef48f7216cc32c7c8196e1600386dc753e4c41543498',
    'b32af739070b0eb510fcd805f95e6a3959ffd570fdd6a7e78e6d4db394ea530f',
    'e46620af6fb5fd7a90bd72aa8022d468e379772bb8801d198a22dc645ea1003e',
    'fb9382e02157d52416a11929bb6f91b35a098d28293210bfac90ae05bf9bd2dd',
    '6cbbcb32188d626ed01860d9bf359a084c5b8d10bcdd7c615b333c5cf2264509',
    '4a57a5125095aef2c97cf8183f153b251b4e7046ddc9a9f3a5c71c8243107307',
    'be6aa08ebc095b552440123387141f905bb2f1189244148de8a46d585219d26c',
    '2814f9308968feffa9e86a4d033cfb0ddaf178b8e05f7237a7c14bbe579360b8',
    '8d129d5d5caa9297b6a696fa942af858573c73e244078c34387ed5f08772b644',
    '2749eaae97250b76dbef11f003e428b5e8aa40246a154787fe203dd43d0908ab',
    '108694ab12cad6479a36d88c9bfb559e5be68565ffc6fc2e387cf5214e10b54b',
    '1f1d884a33f4c133450a33a92c721c40c1d6cf26b9b08c03477db0db3f788589',
    'bf13d074406d7a9f742a9b054ee85ac09e6a1c5825a9b938be8e89e0a69ced70',
    '0ebfc1f6a9933ae54746395a9951e7c95adf1775b26043aa590430257492fda9',
    'af772ea27f1bba30ef9d6a708308b4309ae69bfae270470b9286bd6b252cc0bf',
    'ec9318b070295e4477b2e4dcebc833c7f623e93da6df11561ada25827d5a0656',
    'feb0c165654dca4a66eba70badbb92ff86da3b80462c2af2a031f1d809e62b8f',
    '74a5627d299dabc863afab62512315aceec0c9996d2c9503f26c923745a3923b',
    '66c3131046810d4317f75e60f2e6e36292677fb4beb22888b843ec8827c52aab',
    'b454c1bb6d6f69d8d4a00fd47b96e171fdb13375f9e26084ef60565bb0cbb979',
    '9c80c37f7d23329440d06c1640b2c8c206b20585c38cea612c6efaf9588c559f',
    '836322d3a91c3147dcd47e97285af16d498f5006e05829303474c62c1655b3eb',
    'fd2bd90e1deb7e4bf0024cf58ea006e1004e564090d8f5f66dca2e25e788568e',
    '6b9d3a3286c3f021e15632d86b0202236609c9dbcb5344b2b322284a031aa655',
    '67eb935685cddd224a36ab1c231119f1dd32b5cba43ead97fff704eb3535200e',
    '8126d3e2279747880703bbc0855c3dfab0f7646d478309ca617dca895c570162',
    'c21ead5749ef1c474d3fc636bd6d5133d917c5602dd84ea550f08db813d364c2',
    '2c794be36d7c40d7a60e5ac236c808b5bb2037c6bbc24db9612977c882a568ee',
    '0b7b9073fe8e0ab222eba71a09dc43d659480ae01479987067ff5cd5a8a26af9',
    '50a99403e2c01a6f833f1f5d4502dc9cacc3e029f4eca6b07a1491a432ea8c32',
    '66dd7d7d333c7af11437e7cc1a8fe01254b38fe7b6ed32122503240c05e58863',
    'd17570213910d6ea984c8ac6ebadeb3cc507c5040b7a1fc77f0ba991d3bac7f1',
    'e5ef6b07f2f31289a37f2d33198b4180fba43278761fe2f7c4a042e7b49041da',
    '2a38a2776510d060f49018dfb11220cff763607587356361b8445a40901699bf',
    '020c2ba537094d65aa76b8c480d1f85b8f6287dd21c88705d53bfa8631923fa9',
    '51cadc96e94cdfd23c0a7ce349bc5468ea2fa33c33c4338c015db36a33d1e10a',
    'c8b750421722ee1e8f2612cc6e15f5f9cfbae1da5d13bebdfaeba1ce49627a61',
    '36c6cc590bcaf905b06c0f28cd26862baf622bc6f3c9634c797e977c82fc49c3',
    '405db15f1e19b5d64d0a782b2381c784f288c1e272d24e7483f93082fdaa42b5',
    'dccb78665d7fb43afca470448c7f766b4646e769355207eafbea1077b99270fb',
    'f7a08ff9669972a2e767185832fe7699ecf735c4b37cd6c85ed3e3adaae3741a',
    'f3c336e459b672d2ba19229b7131f44510566e992511c65bc66a61629da4ade0',
    'bdd0254eff7df0bc0d3f33bc9a6c07e52453ca7c2b3610106317e9135e11366d',
    '0c102163fd3d7a1d232334924901746e629320542d3f06aadba1e9d4faf0a37a',
    '27e3a5f3fd73a2d6d1486d6e52b7120ba5e74e8d6558dee360632c1f6f9ceb27',
    '5c508704b642a22add50b7e9f3e68bc4b37936a638c25d5a66051dea44e4fe5f',
    'cc27f3d4573d394c7904361edee0a558db16863f797c8ea9336bcc9d37485eb6',
    'bced75965e19e5d059df0a5d2178298e451f11d0a372b4d066ef018d72a1ceaf',
    '15ad95c53a3ec7c483eded3ce7601b9a8ba8554b39e353b96e7c74eead654f04',
    'cb0e00fa5b9fe292006a34e72aba53b25a063a6c5d6029dac6476ffd957077fe',
    '6f73006551ceb53cd3a437e64029d114ec562e352e67e9d675c20eda1cb8357b',
    '796a63e84196a96003c9e5b8a4ea4fd0d6e3c7bca600e2e00801f7753ad5a97a',
    'defe591c3e08a0d9087d3d9db2aa9ca6d791e0b6f92b68212be7d778d2198020',
    'da4e2cf7ef7c8c9bfd29a8ac34060a65bb8efff6c43c508a885b5d9eed1c4810',
    '304944e5fff09da37e2b00a5d0544c32358bc23f6f2b5baf52a33b7dc00216b3',
    'b9b78fa0b5d36137dcbc7697193d6ab13aad3a34913fc82ffe63a49537667a60',
    '1c8613431b470e752f2990e9be2c6c6efacbb3866791d2858fa408308dcdf049',
    '888891ce03c62a41b87dd079dae3ba53e731aa6e54ece60d4bd6a91b2fb464fb',
    'ad86b5b73cc82692c5bd554a91cf704e425853c1b3f4266b406b935400ab96be',
    '72ca048c9066f8f0be851840fe9fc59476d21143e0b55849ee1a58c8c4b7da8d',
    '85c90ba1d74d3d380cb0ffdac027ad12628aec3a337d32d25f25c07ee4963b6f',
    '381e4804feac3aba82d63a16b25372b7869a0b0165c6b5872be917bbd78cc46f',
    '2820ae9349899b3b4114b1784abd9f7eab61309f18fac6f2694ba233d51a6855',
    '7c73b116d8066dcfce13b3887fd45b0cd93b033c0118186166292e891b405125',
    'b21724386c676f3ceecdfbf139f3d438e9b8bf6dd085720a71a270401b96ef9b',
    '8e93564b0ad34aef805dc8165b9db8a1016dda5fb0d7ec3da3c3001764595c6b',
    'c12252412e7c841d2dcb8a47c30044ee90cb5ad276c4179fbd245dff927a9a9a',
    'cafa546829aad20f9b37b7307d16a2512fec3b3ccd17596d2e32126923592246',
    '4507669b48c9c95c63649cffa982031fa8d314ab0fb5a8abf608ece20c74cd86',
    '7d5d32a1f80bee1a459611678b328948a6a04851d4673ea1185d9cac82fc85e6',
    'ca5f61e17ae7dadc5a91ad371c99739799d62e8e23a89f3c0fc83553b5ec5c1a',
    '761a433e01cd6a58d50abecee0efcd47db4874986ea3d463802afd3362057992',
    '56e6d89e000a01d96471f5c47b351b4457a1441b2568df984676df6e234beeb5',
    '3e1df69d7bcd69985224bdf17f91cfcae89aeb6748fb649bf0567ab3f2fd97ed',
    'de69c032ad3424803712c9df79acc53e6824438d9e3da56db88cb9625592fbb0',
    '5ab1081ac4aed8a256930e1e9a63da526534aafc3b6e9762995d7ce72e8ffd99',
    'cfa17682f1e7d22305d5ac4d08ec9e3b0a52b7d4e17e92b622620860622d419e',
    '8905d174c6b9502c2b9b7aa7cbef7c061a4875a48ce2db1ebfffb5da49022d53',
]

def git_sha(data: bytes) -> str:
    hdr = b'blob ' + str(len(data)).encode() + b'\0'
    return hashlib.sha1(hdr + data).hexdigest()

def _block_mismatches_017(data: bytes):
    if len(data) != 8000:
        return list(range(80))
    out=[]
    for i, target in enumerate(BLOCK_HASHES_017):
        block=data[i*100:(i+1)*100]
        if hashlib.sha256(block).hexdigest()!=target:
            out.append(i)
    return out

def _repair_one_substitution_in_block(data: bytes, block_index: int):
    start=block_index*100
    end=start+100
    target=BLOCK_HASHES_017[block_index]
    block=bytearray(data[start:end])
    for rel, old in enumerate(block):
        for ch in B64_ALPHABET:
            if ch==old:
                continue
            block[rel]=ch
            if hashlib.sha256(block).hexdigest()==target:
                fixed=data[:start]+bytes(block)+data[end:]
                print(f'part-017: repaired substituted byte at {start+rel}')
                return fixed
        block[rel]=old
    return None

def repair_part017(data: bytes, target_sha: str) -> bytes:
    if len(data)==8000 and git_sha(data)==target_sha:
        print('part-017: exact')
        return data
    candidates=[]
    if len(data)==8001:
        for pos in range(len(data)):
            cand=data[:pos]+data[pos+1:]
            bad=_block_mismatches_017(cand)
            candidates.append((len(bad),pos,bad,cand))
        candidates.sort(key=lambda x:x[0])
        best=candidates[0][0]
        print(f'part-017: best deletion candidates mismatch_blocks={best}')
        for bad_count,pos,bad,cand in candidates:
            if bad_count>best+1:
                break
            fixed=cand
            ok=True
            for bi in bad:
                repaired=_repair_one_substitution_in_block(fixed,bi)
                if repaired is None:
                    ok=False
                    break
                fixed=repaired
            if ok and git_sha(fixed)==target_sha:
                print(f'part-017: repaired one extra byte at {pos} with block-guided recovery')
                return fixed
    elif len(data)==8000:
        fixed=data
        bad=_block_mismatches_017(fixed)
        for bi in bad:
            repaired=_repair_one_substitution_in_block(fixed,bi)
            if repaired is None:
                break
            fixed=repaired
        if git_sha(fixed)==target_sha:
            print('part-017: repaired block-guided substitutions')
            return fixed
    raise RuntimeError(f'part-017: block-guided recovery failed len={len(data)} sha={git_sha(data)}')

def repair_one(data: bytes, target_len: int, target_sha: str, label: str) -> bytes:
    if label == 'part-017':
        return repair_part017(data,target_sha)
    if len(data) == target_len and git_sha(data) == target_sha:
        print(f'{label}: exact')
        return data
    if len(data) == target_len + 1:
        for pos in range(len(data)):
            cand = data[:pos] + data[pos+1:]
            if git_sha(cand) == target_sha:
                print(f'{label}: repaired one extra byte at {pos}')
                return cand
    elif len(data) == target_len - 1:
        for pos in range(target_len):
            prefix, suffix = data[:pos], data[pos:]
            for ch in B64_ALPHABET:
                cand = prefix + bytes((ch,)) + suffix
                if git_sha(cand) == target_sha:
                    print(f'{label}: repaired one missing byte at {pos}')
                    return cand
    elif len(data) == target_len:
        for pos, old in enumerate(data):
            for ch in B64_ALPHABET:
                if ch == old: continue
                cand = data[:pos] + bytes((ch,)) + data[pos+1:]
                if git_sha(cand) == target_sha:
                    print(f'{label}: repaired one substituted byte at {pos}')
                    return cand
    raise RuntimeError(f'{label}: unrecoverable transport mismatch len={len(data)} target={target_len} sha={git_sha(data)}')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--parts-dir', default='stage140_transport_release')
    ap.add_argument('--archive', default='Stage140000-CLOUD-V5.tar.xz')
    ap.add_argument('--extract-dir')
    args=ap.parse_args()
    d=pathlib.Path(args.parts_dir)
    chunks=[]
    for key,(target_len,target_sha) in EXPECTED.items():
        if key == '005' and (d/'part-005-0.b64').exists() and (d/'part-005-1.b64').exists():
            data=(d/'part-005-0.b64').read_bytes()+(d/'part-005-1.b64').read_bytes()
        else:
            p=d/f'part-{key}.b64'
            if not p.exists(): raise FileNotFoundError(p)
            data=p.read_bytes()
        chunks.append(repair_one(data,target_len,target_sha,f'part-{key}'))
    encoded=b''.join(chunks)
    if len(encoded)!=ENCODED_SIZE: raise RuntimeError(f'encoded length {len(encoded)} != {ENCODED_SIZE}')
    archive=base64.b64decode(encoded, validate=True)
    if len(archive)!=ARCHIVE_SIZE: raise RuntimeError(f'archive size {len(archive)} != {ARCHIVE_SIZE}')
    sha=hashlib.sha256(archive).hexdigest()
    if sha!=ARCHIVE_SHA256: raise RuntimeError(f'archive sha256 {sha} != {ARCHIVE_SHA256}')
    out=pathlib.Path(args.archive); out.write_bytes(archive)
    print(f'TRANSPORT_SHA256_PASS {sha}')
    if args.extract_dir:
        dest=pathlib.Path(args.extract_dir); dest.mkdir(parents=True,exist_ok=True)
        with tarfile.open(out,'r:xz') as tf: tf.extractall(dest, filter='data')
        print(f'EXTRACT_PASS {dest}')
if __name__=='__main__':
    try: main()
    except Exception as e:
        print(f'TRANSPORT_GATE_FAIL: {e}', file=sys.stderr); raise
