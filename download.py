import instaloader

def download_post(post_url, save_dir="downloads"):
    loader = instaloader.Instaloader(
        download_videos=True,
        dirname_pattern=save_dir
    )
    shortcode = post_url.strip("/").split("/")[-1]
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    loader.download_post(post, target=save_dir)
    return f"Downloaded: {post_url} to {save_dir}"