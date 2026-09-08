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

def git_sha(data: bytes) -> str:
    hdr = b'blob ' + str(len(data)).encode() + b'\0'
    return hashlib.sha1(hdr + data).hexdigest()

def repair_one(data: bytes, target_len: int, target_sha: str, label: str) -> bytes:
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
