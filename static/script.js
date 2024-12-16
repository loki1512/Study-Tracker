document.addEventListener('DOMContentLoaded', () => {
    const subjectDropdown = document.getElementById('subject');
    const otherSubjectContainer = document.getElementById('other-subject-container');
    const otherSubjectInput = document.getElementById('other-subject');
    const descriptionInput = document.getElementById('description');

    subjectDropdown.addEventListener('change', () => {
        if (subjectDropdown.value === 'Others') {
            otherSubjectContainer.style.display = 'block';
        } else {
            otherSubjectContainer.style.display = 'none';
            otherSubjectInput.value = ''; // Clear the input field
        }
    });

    let startTime = null;

    document.getElementById('start-session').addEventListener('click', () => {
        startTime = new Date();
        document.getElementById('start-session').disabled = true;
        document.getElementById('end-session').disabled = false;
        alert(`Session started at ${startTime.toLocaleTimeString()}`);
    });

    document.getElementById('end-session').addEventListener('click', async () => {
        if (!startTime) return;

        const endTime = new Date();
        const subject = subjectDropdown.value === 'Others' ? otherSubjectInput.value : subjectDropdown.value;
        const description = descriptionInput.value.trim();

        const sessionData = {
            start: startTime.toLocaleTimeString(),
            end: endTime.toLocaleTimeString(),
            subject: subject,
            description: description
        };

        try {
            const response = await fetch('https://study-tracker-arcb.onrender.com/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(sessionData)
            });

            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            const result = await response.json();
            if (result.message) {
                alert(result.message);
                fetchSessions(); // Refresh streak and recent sessions dynamically
            } else {
                alert('Error logging session!');
            }
        } catch (error) {
            console.error('Error logging session:', error);
            alert('Error logging session! Please check the console for details.');
        }

        startTime = null;
        document.getElementById('start-session').disabled = false;
        document.getElementById('end-session').disabled = true;
    });

    // Function to fetch streak and recent sessions
    async function fetchSessions() {
        try {
            const response = await fetch('https://study-tracker-arcb.onrender.com/get_sessions');
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            const data = await response.json();

            // Update streak
            document.getElementById('streak').textContent = data.streak;

            // Update recent sessions
            const sessionsTable = document.getElementById('recent-sessions');
            sessionsTable.innerHTML = ''; // Clear existing rows

            data.recent_sessions.forEach(session => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${session[0]}</td>
                    <td>${session[1]}</td>
                    <td>${session[2]}</td>
                    <td>${session[3]}</td>
                    <td>${session[4]}</td>
                `;
                sessionsTable.appendChild(row);
            });
        } catch (error) {
            console.error('Error fetching sessions:', error);
        }
    }

    // Initial fetch when the page loads
    fetchSessions();
});
