const express = require('express');
const ytdl = require('ytdl-core');
const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static('public')); // Serve frontend files

app.post('/download', async (req, res) => {
    try {
        const { url } = req.body;
        
        // Validate URL
        if (!ytdl.validateURL(url)) {
            return res.status(400).json({ error: 'Invalid YouTube URL' });
        }
        
        // Get video info
        const info = await ytdl.getInfo(url);
        
        // Send video info to frontend
        res.json({
            success: true,
            videoInfo: {
                title: info.videoDetails.title,
                thumbnail: info.videoDetails.thumbnails[0].url,
                formats: info.formats.map(f => ({
                    quality: f.qualityLabel || 'Audio',
                    format: f.container,
                    size: 'Unknown' // Would need to calculate
                }))
            }
        });
    } catch (error) {
        res.status(500).json({ error: 'Server error' });
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});