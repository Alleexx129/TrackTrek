document.addEventListener("DOMContentLoaded", function() {
    // License button event listener
    document.getElementById("license").addEventListener("click", function() {
        window.electronAPI.openNewWindow('https://raw.githubusercontent.com/Alleexx129/TrackTrek/refs/heads/main/LICENSE');
    });

    // Source code button event listener
    document.getElementById("sourceCode").addEventListener("click", function() {
        window.electronAPI.openNewWindow('https://github.com/Alleexx129/TrackTrek/');
    });

    // Download button event listener
    document.getElementById("downloadButton").addEventListener("click", function() {
        const keyword = document.querySelector('.titleInputText').value;
        searchVideos(keyword);
        document.getElementById("downloadButton").disabled = true;
    });

    async function searchVideos(keyword) {
        try {
            // Call Python script to search for videos and return titles
            const results = await window.electronAPI.searchVideos(keyword);
            
            let videoTitles;
            try {
                // Attempt to parse the results as JSON
                videoTitles = JSON.parse(results);
            } catch (parseError) {
                // If parsing fails, display the raw output as text
                console.log("Raw response:", results);
                document.getElementById("output").textContent = results;
                return;
            }
    
            // Clear previous results and display the parsed video titles as buttons
            const newspace = document.getElementById("newspace");
            newspace.innerHTML = ''; // Clear previous results
            
            if (Array.isArray(videoTitles)) {
                videoTitles.forEach(video => {
                    const button = document.createElement('button');
                    button.textContent = video.title;
                    button.className = 'videoButton';
                    button.onclick = () => downloadVideo(video.title); // Pass index to download function
                    newspace.appendChild(button);
                });
            } else {
                console.log(videoTitles);
                downloadVideo(videoTitles.title);
            };
        } catch (error) {
            console.error("Error loading videos:", error);
        }
    }
    

    async function downloadVideo(index) {
        try {
            // Call Python script to download the selected video by index
            const result = await window.electronAPI.downloadVideo(index);
            console.log(result);
        } catch (error) {
            console.error("Error downloading video:", error);
        }
    }  
});
