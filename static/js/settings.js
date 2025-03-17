
// Function to open the modal with family details
function openFamilyModal(familyId) {
  fetch(`/membership/family/${familyId}/detail/`)  // Endpoint to fetch family details
      .then(response => response.json())
      .then(data => {
          // Populate modal with family data
          document.getElementById('modalFamilyName').textContent = data.family_name;
          document.getElementById('modalAddress').textContent = data.address || 'Not provided';
          document.getElementById('modalPhone').textContent = data.phone_number || 'Not provided';
          document.getElementById('modalHead').textContent = data.head_of_family || 'Not assigned';
          document.getElementById('modalMembersCount').textContent = data.members_count;

          // Populate members list with detailed information
          const membersList = document.getElementById('modalMembersList');
          membersList.innerHTML = data.members.map(member => `
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div class="flex items-center justify-between cursor-pointer" onclick="toggleMemberDetails(this)">
                      <div class="flex items-center space-x-3">
                          <div class="bg-indigo-500/10 p-2 rounded-lg">
                              <i class="fas fa-user text-indigo-500"></i>
                          </div>
                          <div>
                              <p class="font-medium text-gray-900 dark:text-white">${member.name}</p>
                              <p class="text-sm text-gray-500 dark:text-gray-400">${member.role}</p>
                          </div>
                      </div>
                      <i class="fas fa-chevron-down text-gray-500 dark:text-gray-400 transform transition-transform"></i>
                  </div>
                  <div class="member-details mt-4 space-y-2 hidden">
                      <div class="flex items-center space-x-3">
                          <i class="fas fa-phone text-blue-500"></i>
                          <p class="text-gray-700 dark:text-gray-300">${member.phone || 'Not provided'}</p>
                      </div>
                      <div class="flex items-center space-x-3">
                          <i class="fas fa-map-marker-alt text-green-500"></i>
                          <p class="text-gray-700 dark:text-gray-300">${member.address || 'Not provided'}</p>
                      </div>
                       <div class="flex items-center space-x-3">
                          <i class="fas fa-envelope text-fuchsia-600"></i>
                          <p class="text-gray-700 dark:text-gray-300">${member.email || 'Not provided'}</p>
                      </div>
                      <div class="flex items-center space-x-3">
                          <i class="fas fa-calendar-alt text-purple-500"></i>
                          <p class="text-gray-700 dark:text-gray-300">Joined: ${member.date_joined}</p>
                      </div>
                      <div class="flex items-center space-x-3">
                          <i class="fas fa-water text-indigo-500"></i>
                          <p class="text-gray-700 dark:text-gray-300">Baptized: ${member.baptized ? 'Yes' : 'No'}</p>
                      </div>
                  </div>
              </div>
          `).join('');

          // Show modal
          const modal = document.getElementById('familyModal');
          const content = document.getElementById('modalContent');
          modal.classList.remove('hidden');
          setTimeout(() => {
              content.classList.add('modal-animate-in');
          }, 10);
      })
      .catch(error => {
          console.error('Error fetching family details:', error);
          alert('Failed to load family details. Please try again.');
      });
}

// Function to close the modal
function closeFamilyModal() {
  const modal = document.getElementById('familyModal');
  const content = document.getElementById('modalContent');
  
  content.classList.remove('modal-animate-in');
  setTimeout(() => {
      modal.classList.add('hidden');
  }, 200);
}

// Function to toggle member details
function toggleMemberDetails(element) {
  const details = element.nextElementSibling;
  const chevron = element.querySelector('.fa-chevron-down');
  
  details.classList.toggle('hidden');
  chevron.classList.toggle('rotate-180');
}

// Close modal when clicking outside
// document.getElementById('familyModal').addEventListener('click', (e) => {
//   if(e.target === document.getElementById('familyModal')) {
//       closeFamilyModal();
//   }
// });

// Close modal when clicking outside
document.getElementById('familyModal').addEventListener('click', (e) => {
  const modalContent = document.getElementById('modalContent');
  // Check if the click is outside the modal content
  if (!modalContent.contains(e.target)) {
      closeFamilyModal();
  }
});

