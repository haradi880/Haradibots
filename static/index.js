        document.addEventListener('DOMContentLoaded', function() {
            // Get all elements
            const menuToggle = document.getElementById('menuToggle');
            const navLinks = document.getElementById('navLinks');
            const userBtn = document.getElementById('userBtn');
            const userMenu = document.getElementById('userMenu');
            const dropdownIcon = document.getElementById('dropdownIcon');
            const navItems = document.querySelectorAll('.nav-links a');

            // Toggle mobile menu
            menuToggle.addEventListener('click', function(e) {
                e.stopPropagation();
                navLinks.classList.toggle('open');
                const icon = menuToggle.querySelector('i');
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            });

            // Toggle user menu
            userBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                userMenu.classList.toggle('show');
                dropdownIcon.style.transform = userMenu.classList.contains('show') 
                    ? 'rotate(180deg)' 
                    : 'rotate(0)';
            });

            // Close menus when clicking outside
            document.addEventListener('click', function(e) {
                // Close mobile menu if clicking outside
                if (!menuToggle.contains(e.target) && !navLinks.contains(e.target)) {
                    navLinks.classList.remove('open');
                    const icon = menuToggle.querySelector('i');
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }

                // Close user menu if clicking outside
                if (!userBtn.contains(e.target) && !userMenu.contains(e.target)) {
                    userMenu.classList.remove('show');
                    dropdownIcon.style.transform = 'rotate(0)';
                }
            });

            // Close mobile menu when clicking a nav item
            navItems.forEach(item => {
                item.addEventListener('click', function() {
                    navLinks.classList.remove('open');
                    const icon = menuToggle.querySelector('i');
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                });
            });

            // Prevent clicks inside menus from closing them
            navLinks.addEventListener('click', function(e) {
                e.stopPropagation();
            });

            userMenu.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        });
            document.addEventListener('DOMContentLoaded', function() {
        // Typing Effect
        const typingElement = document.querySelector('.typing-effect');
        const words = ['Machine Learning', 'Deep Learning', 'AI Research', 'Neural Networks', 'Data Science'];
        let wordIndex = 0;
        let charIndex = 0;
        let isDeleting = false;
        let isEnd = false;
        
        function type() {
            const currentWord = words[wordIndex];
            const currentChar = currentWord.substring(0, charIndex);
            
            typingElement.textContent = currentChar;
            
            if (!isDeleting && charIndex < currentWord.length) {
                // Typing forward
                charIndex++;
                setTimeout(type, 100);
            } else if (isDeleting && charIndex > 0) {
                // Deleting backward
                charIndex--;
                setTimeout(type, 50);
            } else {
                // Change word
                isDeleting = !isDeleting;
                if (!isDeleting) {
                    wordIndex = (wordIndex + 1) % words.length;
                }
                setTimeout(type, 1000);
            }
        }
        
        // Start typing effect
        setTimeout(type, 1000);
        
        // Particle Background
        const canvas = document.getElementById('particleCanvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const particles = [];
        const particleCount = window.innerWidth < 768 ? 30 : 100;
        
        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.size = Math.random() * 3 + 1;
                this.speedX = Math.random() * 1 - 0.5;
                this.speedY = Math.random() * 1 - 0.5;
                this.color = `rgba(255, 255, 255, ${Math.random() * 0.5 + 0.1})`;
            }
            
            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                
                if (this.x < 0 || this.x > canvas.width) {
                    this.speedX = -this.speedX;
                }
                
                if (this.y < 0 || this.y > canvas.height) {
                    this.speedY = -this.speedY;
                }
            }
            
            draw() {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        
        function initParticles() {
            for (let i = 0; i < particleCount; i++) {
                particles.push(new Particle());
            }
        }
        
        function animateParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            for (let i = 0; i < particles.length; i++) {
                particles[i].update();
                particles[i].draw();
            }
            
            // Connect particles
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance < 100) {
                        ctx.strokeStyle = `rgba(255, 255, 255, ${1 - distance / 100})`;
                        ctx.lineWidth = 0.5;
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }
            
            requestAnimationFrame(animateParticles);
        }
        
        initParticles();
        animateParticles();
        
        window.addEventListener('resize', function() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });
        
        // Charts
        const growthCtx = document.getElementById('growthChart').getContext('2d');
        const growthChart = new Chart(growthCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [
                    {
                        label: 'Codes',
                        data: [120, 190, 170, 220, 260, 300],
                        borderColor: '#4361ee',
                        backgroundColor: 'rgba(67, 97, 238, 0.1)',
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Notes',
                        data: [80, 120, 140, 160, 190, 220],
                        borderColor: '#3a0ca3',
                        backgroundColor: 'rgba(58, 12, 163, 0.1)',
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Datasets',
                        data: [50, 70, 90, 110, 130, 150],
                        borderColor: '#f72585',
                        backgroundColor: 'rgba(247, 37, 133, 0.1)',
                        tension: 0.3,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
        
        const progressCtx = document.getElementById('progressChart').getContext('2d');
        const progressChart = new Chart(progressCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                datasets: [{
                    label: 'Resources Used',
                    data: [12, 19, 15, 22, 18, 25, 30],
                    backgroundColor: 'rgba(67, 97, 238, 0.7)',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
        
        // Tab functionality
        const tabBtns = document.querySelectorAll('.tab-btn');
        
        tabBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // Remove active class from all buttons
                tabBtns.forEach(b => b.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Hide all tab panes
                document.querySelectorAll('.tab-pane').forEach(pane => {
                    pane.classList.remove('active');
                });
                
                // Show corresponding pane
                const tabId = this.getAttribute('data-tab');
                document.getElementById(tabId).classList.add('active');
            });
        });
        
        // View toggle in explorer
        const viewBtns = document.querySelectorAll('.view-btn');
        const resourceViews = document.querySelectorAll('.resource-view');
        
        viewBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // Remove active class from all buttons
                viewBtns.forEach(b => b.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Hide all views
                resourceViews.forEach(view => {
                    view.classList.remove('active');
                });
                
                // Show selected view
                const viewType = this.getAttribute('data-view');
                document.querySelector(`.${viewType}-view`).classList.add('active');
            });
        });
        
        // Time filter in dashboard
        const timeFilters = document.querySelectorAll('.time-filter button');
        
        timeFilters.forEach(btn => {
            btn.addEventListener('click', function() {
                // Remove active class from all buttons
                timeFilters.forEach(b => b.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // In a real app, you would update the chart data here
            });
        });
        
        // Example of loading more resources
        const loadMoreBtn = document.querySelector('.load-more');
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', function() {
                // Simulate loading
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
                
                setTimeout(() => {
                    this.textContent = 'Load More';
                    // In a real app, you would append new resources here
                }, 1500);
            });
        }
        
    });
