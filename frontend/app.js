// app.js – handles UI interactions and communicates with Flask backend

document.addEventListener('DOMContentLoaded', () => {
  const trainBtn = document.getElementById('run-train');
  const benchBtn = document.getElementById('run-benchmark');
  const benchmarkOutput = document.getElementById('benchmark-output');
  const metricsChartCtx = document.getElementById('metricsChart').getContext('2d');

  // Custom Cursor Logic
  const cursor = document.querySelector('.custom-cursor');
  let mouse = { x: null, y: null };
  if (cursor) {
    document.addEventListener('mousemove', (e) => {
      cursor.style.left = e.clientX + 'px';
      cursor.style.top = e.clientY + 'px';
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    });
    document.addEventListener('mousedown', () => cursor.classList.add('active'));
    document.addEventListener('mouseup', () => cursor.classList.remove('active'));
    document.addEventListener('mouseleave', () => {
      cursor.style.opacity = '0';
      mouse.x = null;
      mouse.y = null;
    });
    document.addEventListener('mouseenter', () => cursor.style.opacity = '1');
  }

  // Interactive Particle Engine
  const canvas = document.getElementById('particle-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    let particlesArray = [];
    let numberOfParticles = (canvas.width * canvas.height) / 15000;
    if (numberOfParticles > 80) numberOfParticles = 80;
    
    class Particle {
      constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.directionX = (Math.random() * 1) - 0.5;
        this.directionY = (Math.random() * 1) - 0.5;
        this.size = Math.random() * 2 + 1;
      }
      update() {
        if (this.x > canvas.width || this.x < 0) this.directionX = -this.directionX;
        if (this.y > canvas.height || this.y < 0) this.directionY = -this.directionY;
        
        // Dodge cursor
        if (mouse.x != null && mouse.y != null) {
          let dx = mouse.x - this.x;
          let dy = mouse.y - this.y;
          let distance = Math.sqrt(dx*dx + dy*dy);
          if (distance < 120) {
            this.x -= dx/20;
            this.y -= dy/20;
          }
        }
        
        this.x += this.directionX;
        this.y += this.directionY;
        this.draw();
      }
      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(6, 182, 212, 0.5)';
        ctx.fill();
      }
    }
    
    function initParticles() {
      particlesArray = [];
      for (let i = 0; i < numberOfParticles; i++) {
        particlesArray.push(new Particle());
      }
    }
    
    function animateParticles() {
      requestAnimationFrame(animateParticles);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].update();
      }
      connectParticles();
    }
    
    function connectParticles() {
      for (let a = 0; a < particlesArray.length; a++) {
        for (let b = a; b < particlesArray.length; b++) {
          let distance = ((particlesArray[a].x - particlesArray[b].x) * (particlesArray[a].x - particlesArray[b].x))
            + ((particlesArray[a].y - particlesArray[b].y) * (particlesArray[a].y - particlesArray[b].y));
          if (distance < 15000) {
            let opacity = 1 - (distance/15000);
            ctx.strokeStyle = `rgba(225, 29, 72, ${opacity * 0.5})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
            ctx.lineTo(particlesArray[b].x, particlesArray[b].y);
            ctx.stroke();
          }
        }
      }
    }
    
    window.addEventListener('resize', () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initParticles();
    });
    
    initParticles();
    animateParticles();
  }

  // Carousel Logic
  const track = document.getElementById('carousel-track');
  const nextBtn = document.getElementById('next-card');
  const prevBtn = document.getElementById('prev-card');
  let currentSlide = 0;
  
  function updateCarousel() {
    const cards = document.querySelectorAll('.carousel-card');
    if (cards.length === 0) return;
    const cardWidth = cards[0].getBoundingClientRect().width;
    const gap = 32; // 2rem gap
    const moveAmount = (cardWidth + gap) * currentSlide;
    track.style.transform = `translateX(-${moveAmount}px)`;
  }

  nextBtn.addEventListener('click', () => {
    const cards = document.querySelectorAll('.carousel-card');
    const visibleCards = window.innerWidth <= 768 ? 1 : window.innerWidth <= 1024 ? 2 : 3;
    if (currentSlide < cards.length - visibleCards) {
      currentSlide++;
      updateCarousel();
    }
  });

  prevBtn.addEventListener('click', () => {
    if (currentSlide > 0) {
      currentSlide--;
      updateCarousel();
    }
  });

  window.addEventListener('resize', () => {
    currentSlide = 0;
    updateCarousel();
  });

  // Initialize empty chart
  const metricsChart = new Chart(metricsChartCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Episode Reward',
        data: [],
        borderColor: '#e11d48', // neon crimson
        backgroundColor: 'rgba(225, 29, 72, 0.15)',
        borderWidth: 2,
        tension: 0.3,
        fill: true,
        pointBackgroundColor: '#ff0f39',
        pointBorderColor: 'rgba(255,255,255,0.8)',
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#f8fafc', font: { family: 'Outfit' } } }
      },
      scales: {
        x: { 
          title: { display: true, text: 'Episode', color: '#94a3b8' },
          ticks: { color: '#94a3b8' },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        },
        y: { 
          title: { display: true, text: 'Reward', color: '#94a3b8' },
          ticks: { color: '#94a3b8' },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
      }
    }
  });

  // Poll for metric updates every 2 seconds
  let metricsPollInterval = null;
  function startMetricsPolling() {
    if (metricsPollInterval) clearInterval(metricsPollInterval);
    metricsPollInterval = setInterval(async () => {
      try {
        const resp = await fetch('/api/metrics');
        if (!resp.ok) return;
        const data = await resp.json();
        
        // Update badge
        const statusBadge = document.getElementById('metrics-status');
        if (statusBadge) {
          if (data.is_real) {
            statusBadge.textContent = 'Real Data (Trained)';
            statusBadge.className = 'status-badge status-real';
          } else {
            statusBadge.textContent = 'Placeholder Data (Run Training)';
            statusBadge.className = 'status-badge status-fake';
          }
        }

        // Expect {episodes: [..], rewards: [..]}
        metricsChart.data.labels = data.episodes;
        metricsChart.data.datasets[0].data = data.rewards;
        metricsChart.update();
      } catch (e) { console.error(e); }
    }, 2000);
  }

  trainBtn.addEventListener('click', async () => {
    trainBtn.disabled = true;
    benchBtn.disabled = true;
    trainBtn.textContent = 'Training...';
    benchmarkOutput.textContent = 'Training started... Monitoring metrics.';
    
    await fetch('/api/train', { method: 'POST' });
    
    benchmarkOutput.textContent = 'Training completed. Ready to benchmark.';
    trainBtn.textContent = 'Start Training';
    startMetricsPolling();
    trainBtn.disabled = false;
    benchBtn.disabled = false;
  });

  benchBtn.addEventListener('click', async () => {
    benchBtn.disabled = true;
    benchBtn.textContent = 'Running...';
    benchmarkOutput.textContent = 'Running benchmark... comparing RL agent to BloodHound.';
    
    const resp = await fetch('/api/benchmark', { method: 'POST' });
    const result = await resp.text();
    
    benchmarkOutput.textContent = result;
    benchBtn.textContent = 'Run Benchmark';
    benchBtn.disabled = false;
  });

  // Load Graph visualisation
  loadGraph();
  startMetricsPolling(); // Start polling metrics immediately to fetch existing real data
});

function loadGraph() {
  // Fetch graph JSON from backend
  fetch('/api/graph')
    .then(res => res.json())
    .then(data => {
      const cy = cytoscape({
        container: document.getElementById('cy'),
        elements: data,
        style: [
          { 
            selector: 'node', 
            style: { 
              'background-color': '#06b6d4', 
              label: 'data(id)', 
              'color': '#f8fafc', 
              'font-size': '10px',
              'font-family': 'Outfit, sans-serif',
              'font-weight': '400',
              'text-valign': 'bottom',
              'text-margin-y': '6px',
              'text-outline-color': '#0a0a0f',
              'text-outline-width': 2,
              'shadow-color': '#06b6d4',
              'shadow-blur': 15,
              'shadow-opacity': 0.8
            } 
          },
          { 
            selector: 'edge', 
            style: { 
              'width': 1.5, 
              'line-color': 'rgba(225, 29, 72, 0.4)', 
              'target-arrow-color': 'rgba(225, 29, 72, 0.6)', 
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier'
            } 
          }
        ],
        layout: { 
          name: 'cose', 
          idealEdgeLength: 100, 
          nodeOverlap: 20,
          padding: 30,
          animate: false
        }
      });
    })
    .catch(err => console.error('Failed to load graph', err));
}
