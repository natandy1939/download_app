const style = document.createElement('style');
style.textContent = `
  #mab-ext-container {
    position: fixed;
    right: 20px;
    bottom: 20px;
    z-index: 99999;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 8px;
    background: rgba(20, 20, 20, 0.5);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
  }
  .mab-glass-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 8px;
    border-radius: 10px;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .mab-glass-btn:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: scale(1.1);
  }
  .mab-glass-btn:active {
    transform: scale(0.9);
  }
  .mab-glass-btn svg {
    width: 20px;
    height: 20px;
    stroke: #ffffff;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
    fill: none;
  }
`;
document.head.appendChild(style);

function injectMenu() {
    if (document.getElementById('mab-ext-container')) return;

    const container = document.createElement('div');
    container.id = 'mab-ext-container';

    const copyBtn = document.createElement('button');
    copyBtn.className = 'mab-glass-btn';
    copyBtn.title = "Copy clean link";
    copyBtn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`;
    
    copyBtn.onclick = () => {
        const urlObj = new URL(window.location.href);
        const videoId = urlObj.searchParams.get('v');
        let cleanUrl = videoId ? `https://www.youtube.com/watch?v=${videoId}` : (urlObj.origin + urlObj.pathname);
        navigator.clipboard.writeText(`!{video}${cleanUrl}`);
    };

    const playerBtn = document.createElement('button');
    playerBtn.className = 'mab-glass-btn';
    playerBtn.title = "Launch Player";
    playerBtn.innerHTML = `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><polygon points="10 8 16 12 10 16 10 8"></polygon></svg>`;
    
    playerBtn.onclick = () => { window.open('http://localhost:8000/', '_blank'); };

    container.appendChild(copyBtn);
    container.appendChild(playerBtn);
    document.body.appendChild(container);
}

setInterval(injectMenu, 1500);