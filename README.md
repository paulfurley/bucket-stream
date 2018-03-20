# CertStream Message Processor

**Process certificate update messages from Certificate Transparency.**

This tool simply listens to various certificate transparency logs (via certstream) and attempts to find public S3 buckets from permutations of the certificates domain name.

Thanks to [bucket-stream](https://github.com/eth0izzle/bucket-stream) for the foundation.

## Installation

Python 3.4+ and pip3 are required. Then just:

1. `git clone https://github.com/eth0izzle/bucket-stream.git`
2. *(optional)* Create a virtualenv with `pip3 install virtualenv && virtualenv .virtualenv && source .virtualenv/bin/activate`
2. `pip3 install -r requirements.txt`
3. `python3 monitor.py`

## Usage

Simply run `python3 bucket-stream.py`.

If you provide AWS access and secret keys in `config.yaml` Bucket Stream will attempt to access authenticated buckets and identity the buckets owner. **Unauthenticated users are severely rate limited.**

    usage: python bucket-stream.py

    Find interesting Amazon S3 Buckets by watching certificate transparency logs.

    optional arguments:
      -h, --help            Show this help message and exit
      --only-interesting    Only log 'interesting' buckets whose contents match
                            anything within keywords.txt (default: False)
      --skip-lets-encrypt   Skip certs (and thus listed domains) issued by Let's
                            Encrypt CA (default: False)
      -t , --threads        Number of threads to spawn. More threads = more power.
                            Limited to 5 threads if unauthenticated.
                            (default: 20)
      --ignore-rate-limiting
                            If you ignore rate limits not all buckets will be
                            checked (default: False)
      -l, --log             Log found buckets to a file buckets.log (default:
                            False)

## License

MIT. See LICENSE
