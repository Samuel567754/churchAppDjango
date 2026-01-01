// import AOS from 'aos';
// // Optionally, pass in your configuration options
// AOS.init();

     // Attach event listener to each delete button
function confirmDeletefamily(pk) {
    Swal.fire({
        title: "Are you sure?",
        text: "This family will be permanently deleted along with its members since you are the head, are you willing to continue or edit family to change this if necessary!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Yes, delete it!",
        cancelButtonText: "Cancel",
        background: document.documentElement.classList.contains('dark') ? '#333' : '#fff', // Dark mode background
        color: document.documentElement.classList.contains('dark') ? '#fff' : '#000', // Dark mode text color
    }).then((result) => {
        if (result.isConfirmed) {
        // Submit the hidden form
        document.getElementById("delete-form-" + pk).submit();
        }
    });
    }



function confirmDelete(pk) {
    Swal.fire({
      title: "Are you sure?",
      text: "This prayer request will be permanently deleted!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#3085d6",
      confirmButtonText: "Yes, delete it!",
      cancelButtonText: "Cancel",
      background: document.documentElement.classList.contains('dark') ? '#333' : '#fff', // Dark mode background
      color: document.documentElement.classList.contains('dark') ? '#fff' : '#000', // Dark mode text color
    }).then((result) => {
      if (result.isConfirmed) {
        // Submit the hidden form
        document.getElementById("delete-form-" + pk).submit();
      }
    });
  }
  
  function confirmDeleteNotification(pk) {
    Swal.fire({
      title: "Are you sure?",
      text: "This notification will be permanently deleted!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#3085d6",
      confirmButtonText: "Yes, delete it!",
      cancelButtonText: "Cancel",
      background: document.documentElement.classList.contains('dark') ? '#333' : '#fff', // Dark mode background
      color: document.documentElement.classList.contains('dark') ? '#fff' : '#000', // Dark mode text color
    }).then((result) => {
      if (result.isConfirmed) {
        document.getElementById("delete-form-notification-" + pk).submit();
      }
    });
  }


async function openMinistryModal(ministrySlug) {
    try {
      // Fetch ministry details using the namespaced URL
      const response = await fetch(`/membership/dashboard/ministries/${ministrySlug}/`);
      if (!response.ok) throw new Error("Failed to fetch ministry details");
  
      const data = await response.json();
  
      // Populate modal fields with fetched data
      document.getElementById("modalTitle").innerText = data.name || "No title available";
      document.getElementById("modalDescription").innerText = data.description || "";
      document.getElementById("modalLeader").innerText = data.leader || "Not assigned";
  
      // Build the members list safely
      const membersContainer = document.getElementById("modalMembers");
      if (Array.isArray(data.members) && data.members.length > 0) {
        membersContainer.innerHTML = `<ul class="list-disc pl-4">
          ${data.members.map(member => `<li>${member}</li>`).join("")}
        </ul>`;
      } else {
        membersContainer.textContent = "No members assigned yet.";
      }
  
      // Prepare to set image with a fallback
      const modalImage = document.getElementById("modalImage");
      const fallbackImage = "/static/images/offer_6.jpg"; // A valid fallback image
  
      // Log the image URL
      console.log("Image URL:", data.image_url);
  
      // Set up image load and error handlers BEFORE setting src
      modalImage.onload = () => {
        console.log("Image loaded successfully");
        modalImage.classList.remove("opacity-0");
        // Clear onerror after successful load to prevent unwanted re-triggering
        modalImage.onerror = null;
      };
  
      modalImage.onerror = () => {
        console.log("Error loading image. Fallback used.");
        // Remove onerror to avoid infinite loop if fallback fails
        modalImage.onerror = null;
        modalImage.src = fallbackImage;
      };
  
      // Set the image source dynamically based on data
      modalImage.src = data.image_url || fallbackImage;
      console.log("Setting image source to:", modalImage.src);
  
      // Show modal with entrance animation
      const modal = document.getElementById("ministryModal");
      const modalContent = document.getElementById("modalContent");
  
      modal.classList.remove("hidden");
      document.body.classList.add("overflow-hidden");
  
      // Delay removal of starting animation classes to trigger CSS transitions
      setTimeout(() => {
        modalContent.classList.remove("scale-95", "opacity-0");
        modalContent.classList.add("scale-100", "opacity-100");
      }, 50);
    } catch (error) {
      console.error("Error loading ministry details:", error);
      alert("Failed to load ministry details. Please try again.");
    }
  }
  
  window.openMinistryModal = openMinistryModal;
  // Function to close modal
  function closeMinistryModal() {
    const modal = document.getElementById("ministryModal");
    const modalContent = document.getElementById("modalContent");

    modalContent.classList.add("scale-95", "opacity-0");
    document.body.classList.remove("overflow-hidden");

    setTimeout(() => {
      modal.classList.add("hidden");
    }, 200);
  }

  // Close modal on outside click
  document.getElementById("ministryModal").addEventListener("click", (e) => {
    const modal = document.getElementById("ministryModal");
    if (e.target === modal) closeMinistryModal();
  });

  // Close modal on ESC key
  document.addEventListener("keydown", (e) => {
    const modal = document.getElementById("ministryModal");
    if (e.key === "Escape" && !modal.classList.contains("hidden")) {
      closeMinistryModal();
    }
  });




document.addEventListener('DOMContentLoaded', () => {
    const mainContent = document.getElementById('main-content');
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidenav');
    const mobileCloseBtn = document.getElementById('mobile-close-btn');

    // Toggle sidebar on menu button click
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('hidden');
        });
    }

    // Close sidebar when clicking outside or on a link
    document.addEventListener('click', (event) => {
        if (sidebar && menuToggle) {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnMenuToggle = menuToggle.contains(event.target);

            // Close sidebar if clicking outside or on a link (for mobile)
            if (!isClickInsideSidebar && !isClickOnMenuToggle && !sidebar.classList.contains('hidden')) {
                sidebar.classList.add('hidden');
            }
        }
    });

     // Close sidebar on mobile close button click
     if (mobileCloseBtn) {
        mobileCloseBtn.addEventListener('click', function() {
            sidenav.classList.add('hidden');
        });
    }

    // Close sidebar on mobile after navigating via a link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 1024 && sidebar) {
                sidebar.classList.add('hidden');
            }
        });
    });

    // Function to fetch page content (unchanged)
    async function fetchPageContent(url) {
        try {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const html = await response.text();
            const tempContainer = document.createElement('div');
            tempContainer.innerHTML = html;
            const contentElement = tempContainer.querySelector('#main-content');
            if (contentElement) {
                return contentElement.innerHTML;
            } else {
                throw new Error('Content element not found in response');
            }
        } catch (error) {
            console.error('Fetch error:', error);
            return '<p>Failed to load content.</p>';
        }
    }

  


    function setActiveNavLink(activePage) {
        document.querySelectorAll('.nav-link').forEach(link => {
            const linkPage = link.getAttribute('data-page');
    
            // Reset all links to inactive state
            // Mobile styles
            link.classList.remove(
                'border-blue-500', 'text-blue-500', 
                'dark:border-blue-400', 'dark:text-blue-400'
            );
            link.classList.add(
                'border-transparent', 'text-gray-600', 
                'dark:text-gray-300', 'transition-colors', 'duration-200'
            );
    
            // Desktop styles
            link.classList.remove(
                'bg-blue-50', 'text-blue-600', 
                'dark:bg-blue-800/90', 'dark:text-blue-100'
            );
            link.classList.add(
                'hover:bg-gray-50', 'text-gray-600', 
                'dark:hover:bg-gray-700/50', 'dark:text-gray-200'
            );
        });
    
        // Apply active state to the current link
        let activeLink = document.querySelector(`.nav-link[data-page="${activePage}"]`);
        if (activeLink) {
            if (window.innerWidth >= 1024) {
                // Desktop active styles
                activeLink.classList.remove(
                    'hover:bg-gray-50', 'text-gray-600', 
                    'dark:hover:bg-gray-700/50', 'dark:text-gray-200'
                );
                activeLink.classList.add(
                    'bg-blue-50', 'text-blue-600', 
                    'dark:bg-blue-800/90', 'dark:text-blue-100', 'shadow-sm', 
                    'dark:shadow-blue-900/20'
                );
            } else {
                // Mobile active styles
                activeLink.classList.remove(
                    'border-transparent', 'text-gray-600', 
                    'dark:text-gray-300'
                );
                activeLink.classList.add(
                    'border-blue-500', 'text-blue-500', 
                    'dark:border-blue-400', 'dark:text-blue-400'
                );
            }
        }
    }

    // Handle navigation (unchanged)
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            const page = e.currentTarget.dataset.page;
            const url = e.currentTarget.href;

            mainContent.style.opacity = '0';
            try {
                const content = await fetchPageContent(url);
                setTimeout(() => {
                    mainContent.innerHTML = content;
                    setActiveNavLink(page);
                    mainContent.style.opacity = '1';
                }, 200);
            } catch (error) {
                console.error("Error loading:", error);
                mainContent.innerHTML = "<p>Failed to load content.</p>";
                mainContent.style.opacity = '1';
            }
        });
    });

    // Set initial active link based on current path (unchanged)
    const currentPath = window.location.pathname;
    let activePage = 'home';

    document.querySelectorAll('.nav-link').forEach(link => {
        try {
            const url = new URL(link.href, window.location.origin);
            if (url.pathname === currentPath) {
                activePage = link.dataset.page;
            }
        } catch (error) {
            console.error('Invalid URL ', error);
        }
    });

    // Load initial content if not home page (unchanged)
    const activeLink = document.querySelector(`.nav-link[data-page="${activePage}"]`);
    if (activePage !== 'home' && activeLink) {
        const initialUrl = activeLink.getAttribute('href');
        mainContent.style.opacity = '0';
        fetchPageContent(initialUrl).then(content => {
            setTimeout(() => {
                mainContent.innerHTML = content;
                setActiveNavLink(activePage);
                mainContent.style.opacity = '1';
            }, 200);
        });
    } else {
        setActiveNavLink(activePage);
    }
});


document.addEventListener("DOMContentLoaded", function () {
    let notificationCount = 3; // Fetch this count dynamically from backend
    let badge = document.getElementById("notification-badge");

    if (notificationCount > 0) {
        badge.innerText = notificationCount;
        badge.classList.remove("hidden");
    }
});



















