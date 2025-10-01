<!DOCTYPE html>
<html>
<head>
    <title>Your Website Name Link Shortener</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        /* Custom CSS with your branding */
        body {
            font-family: Arial, sans-serif;
            background: #f7f7f7;
            color: #333;
        }
        
        .container {
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .website-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .website-header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        input[type="url"] {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #3498db;
            border-radius: 5px;
            font-size: 16px;
        }
        
        button {
            background: #3498db;
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        
        button:hover {
            background: #2980b9;
        }
        
        .result-box {
            margin-top: 20px;
            padding: 15px;
            background: #ecf5ff;
            border-radius: 5px;
            display: none;
        }
        
        .analytics-table {
            width: 100%;
            margin-top: 20px;
            border-collapse: collapse;
        }
        
        .analytics-table th, 
        .analytics-table td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="website-header">
            <h1>Your Website Name</h1>
            <p>Professional Link Shortening Service</p>
        </div>
        
        <div class="input-section">
            <input type="url" id="originalUrl" placeholder="Enter your long URL here">
            <button onclick="shortenUrl()">Create Short Link</button>
        </div>

        <div class="result-box" id="resultSection">
            <p>Your short URL: 
                <strong>
                    <a id="shortUrl" target="_blank" style="color: #3498db; text-decoration: none;">
                        <span id="domainDisplay">your-website-name.com/</span>
                        <span id="shortCode"></span>
                    </a>
                </strong>
            </p>
            <button onclick="showAnalytics()" style="margin-top: 10px;">View Analytics</button>
        </div>

        <div class="analytics-section" id="analyticsSection" style="display: none;">
            <h2>Link Analytics</h2>
            <p>Total Clicks: <span id="totalClicks">0</span></p>
            <table class="analytics-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Device</th>
                        <th>Browser</th>
                    </tr>
                </thead>
                <tbody id="analyticsData">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Custom domain display - EDIT THIS SECTION
        const CUSTOM_DOMAIN = "your-website-name.com"; // Change this to your actual domain
        
        // Initialize storage
        let links = JSON.parse(localStorage.getItem('shortLinks')) || {};
        let analyticsData = JSON.parse(localStorage.getItem('linkAnalytics')) || {};

        // Generate random short code
        function generateShortCode() {
            return Math.random().toString(36).substring(2, 8);
        }

        // Shorten URL function
        function shortenUrl() {
            const originalUrl = document.getElementById('originalUrl').value;
            if (!originalUrl.startsWith('http')) {
                alert('Please enter a valid URL starting with http/https');
                return;
            }

            const shortCode = generateShortCode();
            const fullShortUrl = `${window.location.origin}/${shortCode}`;

            // Save to storage
            links[shortCode] = originalUrl;
            analyticsData[shortCode] = [];
            
            localStorage.setItem('shortLinks', JSON.stringify(links));
            localStorage.setItem('linkAnalytics', JSON.stringify(analyticsData));

            // Display result
            document.getElementById('resultSection').style.display = 'block';
            document.getElementById('shortUrl').href = fullShortUrl;
            document.getElementById('shortCode').textContent = shortCode;
            document.getElementById('domainDisplay').textContent = `${CUSTOM_DOMAIN}/`;
        }

        // Show analytics
        function showAnalytics() {
            const shortCode = document.getElementById('shortCode').textContent;
            const data = analyticsData[shortCode] || [];

            document.getElementById('totalClicks').textContent = data.length;
            const tbody = document.getElementById('analyticsData');
            tbody.innerHTML = '';

            data.forEach(entry => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${new Date(entry.timestamp).toLocaleString()}</td>
                    <td>${entry.device || 'Desktop'}</td>
                    <td>${entry.browser}</td>
                `;
                tbody.appendChild(row);
            });

            document.getElementById('analyticsSection').style.display = 'block';
        }

        // Handle redirection
        function handleRedirection() {
            const pathSegments = window.location.pathname.split('/');
            const shortCode = pathSegments[pathSegments.length - 1];
            
            if (shortCode && links[shortCode]) {
                // Record visit
                const entry = {
                    timestamp: new Date().toISOString(),
                    browser: navigator.userAgent.split(') ').pop().split(' ')[0],
                    device: /Mobile/i.test(navigator.userAgent) ? 'Mobile' : 'Desktop'
                };

                analyticsData[shortCode].push(entry);
                localStorage.setItem('linkAnalytics', JSON.stringify(analyticsData));

                // Redirect
                window.location.href = links[shortCode];
            }
        }

        // Initial setup
        window.onload = function() {
            // Set custom domain display
            document.querySelectorAll('.domain-placeholder').forEach(element => {
                element.textContent = CUSTOM_DOMAIN;
            });
            
            handleRedirection();
        };
    </script>
</body>
</html>