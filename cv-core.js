
        // Advanced mobile menu toggle function
        let isMenuOpen = false;

        // Mobile Menu Logic
        function toggleMobileMenu() {
            const mobileMenu = document.getElementById('mobileMenu');
            const navToggle = document.getElementById('navToggle');
            const icon = navToggle.querySelector('i');
            
            mobileMenu.classList.toggle('active');
            
            if (mobileMenu.classList.contains('active')) {
                icon.className = 'fas fa-times';
                document.body.style.overflow = 'hidden';
            } else {
                icon.className = 'fas fa-bars';
                document.body.style.overflow = '';
            }
        }

        function closeMobileMenu() {
            const mobileMenu = document.getElementById('mobileMenu');
            const navToggle = document.getElementById('navToggle');
            
            if (mobileMenu.classList.contains('active')) {
                mobileMenu.classList.remove('active');
                if (navToggle) {
                    const icon = navToggle.querySelector('i');
                    icon.className = 'fas fa-bars';
                }
                document.body.style.overflow = '';
            }
        }

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            const mobileMenu = document.getElementById('mobileMenu');
            const navToggle = document.getElementById('navToggle');
            
            if (mobileMenu && mobileMenu.classList.contains('active') && 
                !mobileMenu.contains(event.target) && 
                !navToggle.contains(event.target)) {
                closeMobileMenu();
            }
        });

        // Video play functionality
        function playVideo(playButton) {
            const videoContainer = playButton.parentElement;
            const video = videoContainer.querySelector('video');

            if (video) {
                // Hide the custom play button
                videoContainer.classList.add('playing');

                // Play the video
                video.play().then(() => {
                    console.log('Video started playing');
                }).catch((error) => {
                    console.error('Error playing video:', error);
                    // Show play button again if there's an error
                    videoContainer.classList.remove('playing');

                    // Show error message
                    const errorMsg = document.createElement('div');
                    errorMsg.style.cssText = `
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        background: rgba(255, 0, 0, 0.8);
                        color: white;
                        padding: 10px 20px;
                        border-radius: 8px;
                        font-size: 14px;
                        z-index: 15;
                    `;
                    errorMsg.textContent = 'Video file not found or cannot be played';
                    videoContainer.appendChild(errorMsg);

                    // Remove error message after 3 seconds
                    setTimeout(() => {
                        if (errorMsg.parentElement) {
                            errorMsg.parentElement.removeChild(errorMsg);
                        }
                    }, 3000);
                });

                // Show play button again when video ends or is paused
                video.addEventListener('ended', () => {
                    videoContainer.classList.remove('playing');
                });

                video.addEventListener('pause', () => {
                    videoContainer.classList.remove('playing');
                });
            }
        }

        // Navigation functionality
        document.addEventListener('DOMContentLoaded', function () {
            const navToggle = document.getElementById('navToggle');
            const navLinks = document.getElementById('navLinks');
            const navMenu = document.querySelector('.nav-menu');

            let lastScrollTop = 0;
            let scrollTimeout;

            // Advanced navigation scroll behavior
            window.addEventListener('scroll', function () {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                const scrollDirection = scrollTop > lastScrollTop ? 'down' : 'up';

                // Clear existing timeout
                clearTimeout(scrollTimeout);

                // Add scrolled class when scrolled down
                if (scrollTop > 50) {
                    navMenu.classList.add('scrolled');
                } else {
                    navMenu.classList.remove('scrolled');
                }

                // Hide nav when scrolling down fast, show when scrolling up
                if (scrollDirection === 'down' && scrollTop > 200) {
                    navMenu.classList.add('hidden');
                } else if (scrollDirection === 'up' || scrollTop < 100) {
                    navMenu.classList.remove('hidden');
                }

                // Show nav again after scroll stops
                scrollTimeout = setTimeout(() => {
                    navMenu.classList.remove('hidden');
                }, 1000);

                lastScrollTop = scrollTop;
            });

            // Mobile menu toggle - now handled by onclick in HTML

            // Enhanced smooth scrolling for navigation links
            const links = document.querySelectorAll('.nav-links a, #mobileMenu a');
            links.forEach(link => {
                link.addEventListener('click', function (e) {
                    const href = this.getAttribute('href');
                    if (href && href.startsWith('#')) {
                        e.preventDefault();
                        const targetElement = document.querySelector(href);

                        if (targetElement) {
                            const navHeight = 70; // Height of the fixed nav
                            const elementPosition = targetElement.getBoundingClientRect().top;
                            const offsetPosition = elementPosition + window.pageYOffset - navHeight;

                            window.scrollTo({
                                top: offsetPosition,
                                behavior: "smooth"
                            });
                        }
                        
                        // Close mobile menu if open
                        closeMobileMenu();
                    }
                });
            });



            // Scroll progress indicator (existing functionality)
            window.addEventListener('scroll', function () {
                const scrollProgress = document.getElementById('scrollProgress');
                const scrollTop = window.pageYOffset;
                const docHeight = document.body.scrollHeight - window.innerHeight;
                const scrollPercent = (scrollTop / docHeight) * 100;
                scrollProgress.style.width = scrollPercent + '%';
            });
        });
    