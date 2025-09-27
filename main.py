from downloader import download_post

def main():
    url = input("Paste Instagram link: ")
    try:
        result = download_post(url)
        print(result)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()