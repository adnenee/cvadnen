
        // Scroll progress indicator
        window.addEventListener('scroll', () => {
            const scrollProgress = document.getElementById('scrollProgress');
            const scrollTop = window.pageYOffset;
            const docHeight = document.body.offsetHeight - window.innerHeight;
            const scrollPercent = (scrollTop / docHeight) * 100;
            scrollProgress.style.width = scrollPercent + '%';
        });

        // Floating profile picture animation
        let profileContainer = null;
        let isFloating = false;
        let floatingClone = null;

        function initFloatingProfile() {
            profileContainer = document.querySelector('.profile-img');
            if (!profileContainer) return;

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (!entry.isIntersecting && !isFloating) {
                        // Profile is out of view, create floating version
                        createFloatingProfile();
                    } else if (entry.isIntersecting && isFloating) {
                        // Profile is back in view, remove floating version
                        removeFloatingProfile();
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '-50px 0px 0px 0px'
            });

            observer.observe(profileContainer);
        }

        function createFloatingProfile() {
            if (isFloating || !profileContainer) return;

            // Clone the profile image
            floatingClone = profileContainer.cloneNode(true);
            floatingClone.classList.add('floating');

            // Remove any existing IDs to avoid conflicts
            floatingClone.removeAttribute('id');
            const clonedImg = floatingClone.querySelector('img');
            if (clonedImg) clonedImg.removeAttribute('id');

            // Add enhanced click handler for smooth scroll to top
            floatingClone.style.cursor = 'pointer';
            floatingClone.addEventListener('click', function (e) {
                e.preventDefault();

                // Add visual feedback
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);

                // Smooth scroll to top with enhanced animation
                const startPosition = window.pageYOffset;
                const distance = -startPosition;
                const duration = Math.min(Math.abs(distance) / 2, 1200);
                let start = null;

                function smoothScrollToTop(timestamp) {
                    if (!start) start = timestamp;
                    const progress = timestamp - start;
                    const percentage = Math.min(progress / duration, 1);

                    // Same easing function for consistency
                    const easeInOutCubic = percentage < 0.5
                        ? 4 * percentage * percentage * percentage
                        : 1 - Math.pow(-2 * percentage + 2, 3) / 2;

                    window.scrollTo(0, startPosition + distance * easeInOutCubic);

                    if (progress < duration) {
                        requestAnimationFrame(smoothScrollToTop);
                    }
                }

                requestAnimationFrame(smoothScrollToTop);
            });

            // Add to body
            document.body.appendChild(floatingClone);
            isFloating = true;

            // Trigger animation
            setTimeout(() => {
                floatingClone.style.opacity = '1';
            }, 10);
        }

        function removeFloatingProfile() {
            if (!isFloating || !floatingClone) return;

            // Animate out
            floatingClone.style.opacity = '0';
            floatingClone.style.transform = 'scale(0.5) translateY(-20px)';

            setTimeout(() => {
                if (floatingClone && floatingClone.parentNode) {
                    floatingClone.parentNode.removeChild(floatingClone);
                }
                floatingClone = null;
                isFloating = false;
            }, 300);
        }

        // Initialize when DOM is loaded
        document.addEventListener('DOMContentLoaded', initFloatingProfile);

        // Animate skill bars on scroll
        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const skillBars = entry.target.querySelectorAll('.skill-progress');
                    skillBars.forEach(bar => {
                        const width = bar.style.width;
                        bar.style.width = '0%';
                        setTimeout(() => {
                            bar.style.width = width;
                        }, 200);
                    });
                }
            });
        }, observerOptions);

        // Observe skills section
        const skillsSection = document.querySelector('.sidebar .section:nth-child(3)');
        if (skillsSection) {
            observer.observe(skillsSection);
        }

        // Add smooth scrolling for better UX
        document.documentElement.style.scrollBehavior = 'smooth';

        // Add loading animation
        window.addEventListener('load', () => {
            document.body.style.opacity = '0';
            document.body.style.transition = 'opacity 0.5s ease-in-out';
            setTimeout(() => {
                document.body.style.opacity = '1';
            }, 100);
        });

        // Add hover effects for experience items
        const experienceItems = document.querySelectorAll('.experience-item, .education-item');
        experienceItems.forEach(item => {
            item.addEventListener('mouseenter', () => {
                item.style.transform = 'translateY(-8px)';
            });

            item.addEventListener('mouseleave', () => {
                item.style.transform = 'translateY(-4px)';
            });
        });

        // Handle profile image fallback
        const profileImg = document.querySelector('.profile-img img');
        const profileFallback = document.querySelector('.profile-fallback');

        if (profileImg && profileFallback) {
            // Show fallback if image fails to load
            profileImg.addEventListener('error', () => {
                profileFallback.style.opacity = '1';
                profileImg.style.display = 'none';
            });

            // Hide fallback if image loads successfully
            profileImg.addEventListener('load', () => {
                if (profileImg.naturalWidth > 0) {
                    profileFallback.style.opacity = '0';
                } else {
                    profileFallback.style.opacity = '1';
                    profileImg.style.display = 'none';
                }
            });

            // Check if image is already loaded or failed
            if (profileImg.complete) {
                if (profileImg.naturalWidth === 0) {
                    profileFallback.style.opacity = '1';
                    profileImg.style.display = 'none';
                }
            }
        }

        // Add typing effect to name (optional)
        const nameElement = document.querySelector('.name');
        if (nameElement) {
            const originalText = nameElement.textContent;
            nameElement.textContent = '';
            let i = 0;

            const typeWriter = () => {
                if (i < originalText.length) {
                    nameElement.textContent += originalText.charAt(i);
                    i++;
                    setTimeout(typeWriter, 100);
                }
            };

            setTimeout(typeWriter, 1000);
        }

        // Add parallax effect to floating shapes
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const shapes = document.querySelectorAll('.shape');

            shapes.forEach((shape, index) => {
                const speed = 0.5 + (index * 0.1);
                shape.style.transform = `translateY(${scrolled * speed}px)`;
            });
        });

        // Add click to copy functionality for contact items
        const contactItems = document.querySelectorAll('.contact-item');
        contactItems.forEach(item => {
            item.addEventListener('click', () => {
                const text = item.textContent.trim();
                if (text.includes('@') || text.includes('+')) {
                    navigator.clipboard.writeText(text).then(() => {
                        // Show temporary feedback
                        const originalBg = item.style.background;
                        item.style.background = 'rgba(255, 255, 255, 0.3)';
                        setTimeout(() => {
                            item.style.background = originalBg;
                        }, 300);
                    });
                }
            });
        });
    