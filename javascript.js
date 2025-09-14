// Firebase initialization for client-side operations
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "your-project.firebaseapp.com",
    databaseURL: "https://your-project.firebaseio.com",
    projectId: "your-project",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "YOUR_APP_ID"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Authentication functions
function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({email, password})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/dashboard';
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function signup() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const name = document.getElementById('name').value;
    const referralCode = new URLSearchParams(window.location.search).get('ref') || '';
    
    fetch('/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({email, password, name, referral_code: referralCode})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/dashboard';
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Ad watching functionality
function startAd() {
    fetch('/start_ad', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            startTimer(data.timer);
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function startTimer(seconds) {
    let timer = seconds;
    const timerElement = document.getElementById('adTimer');
    const adContent = document.getElementById('adContent');
    const startButton = document.getElementById('startAdButton');
    
    startButton.disabled = true;
    adContent.style.display = 'block';
    
    const countdown = setInterval(() => {
        timerElement.textContent = timer;
        timer--;
        
        if (timer < 0) {
            clearInterval(countdown);
            completeAd();
        }
    }, 1000);
}

function completeAd() {
    fetch('/complete_ad', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ad_id: 'some_ad_id'})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('earningsDisplay').textContent = 
                '₹' + data.earnings.toFixed(2);
            document.getElementById('adsTodayDisplay').textContent = 
                data.ad_views_today + '/10';
            alert('Ad completed! You earned ₹0.11');
            
            document.getElementById('startAdButton').disabled = false;
            document.getElementById('adContent').style.display = 'none';
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Withdrawal functionality
function requestWithdrawal() {
    const upiId = document.getElementById('upiId').value;
    const amount = document.getElementById('amount').value;
    
    fetch('/withdraw', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({upi_id: upiId, amount: amount})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Withdrawal request submitted successfully. Funds will arrive within 3 business days.');
            window.location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}