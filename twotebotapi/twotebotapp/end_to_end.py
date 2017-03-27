import sys

def interface(hashtag):
    print(hashtag)
    return 


def cli_interface():
    """
    wrapper_cli method that interfaces from commandline to function space
    call the script with: 
    python end_to_end.py <hashtag: Should be hashtag that the stream is filtering on> 
    """
    try:
        hashtag = sys.argv[1]

    except:
        print("usage: {} <hashtag: the hashtag live stream is filering on>".format(sys.argv[0]))
        sys.exit(1)
    interface(hashtag)


if __name__ == "__main__":
    cli_interface()