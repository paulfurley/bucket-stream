# CertStream Message Processor

**Process certificate update messages from Certificate Transparency.**

This tool simply listens to various certificate transparency logs (via certstream) and attempts to find public S3 buckets from permutations of the certificates domain name.

Thanks to [bucket-stream](https://github.com/eth0izzle/bucket-stream) for the foundation.

## Installation

Python 3.4+ and pip3 are required. Then just:

1. `git clone https://github.com/paulfurley/monitor.git`
2. *(optional)* Create a virtualenv with `pip3 install virtualenv && virtualenv .virtualenv && source .virtualenv/bin/activate`
2. `pip3 install -r requirements.txt`
3. `python3 monitor.py`

## Usage

Simply run `python3 monitor.py`.

If you provide AWS access and secret keys in `config.yaml` Bucket Stream will attempt to access authenticated buckets and identity the buckets owner. **Unauthenticated users are severely rate limited.**

    usage: python monitor.py

    Watch certificate transparency logs.

    optional arguments:
      -h, --help            Show this help message and exit
      -t , --threads        Number of threads to spawn. More threads = more power.
                            Limited to 5 threads if unauthenticated.
                            (default: 5)

## License

MIT. See LICENSE
