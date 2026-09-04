let currentData = null;


// =================================
// Elements
// =================================

const urlInput =
    document.getElementById("urlInput");

const analyzeBtn =
    document.getElementById("analyzeBtn");

const analyzeText =
    document.getElementById("analyzeText");

const analyzeLoader =
    document.getElementById("analyzeLoader");

const errorBox =
    document.getElementById("errorBox");

const resultSection =
    document.getElementById("resultSection");

const playlistSection =
    document.getElementById("playlistSection");

const thumbnail =
    document.getElementById("thumbnail");

const videoTitle =
    document.getElementById("videoTitle");

const duration =
    document.getElementById("duration");

const uploader =
    document.getElementById("uploader");

const videoViews =
    document.getElementById("videoViews");

const platformBadge =
    document.getElementById("platformBadge");

const formatSelect =
    document.getElementById("formatSelect");

const qualitySelect =
    document.getElementById("qualitySelect");

const qualityGroup =
    document.getElementById("qualityGroup");


// =================================
// Enter key
// =================================

urlInput.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {
            analyzeVideo();
        }

    }
);


// =================================
// Analyze
// =================================

async function analyzeVideo() {

    const url =
        urlInput.value.trim();


    hideError();


    if (!url) {

        showError(
            "Please paste a YouTube or Facebook URL."
        );

        return;
    }


    setLoading(true);


    resultSection.classList.add("hidden");
    playlistSection.classList.add("hidden");


    try {

        const response =
            await fetch(
                `/api/info?url=${encodeURIComponent(url)}`
            );


        const data =
            await response.json();


        if (!response.ok || !data.success) {

            throw new Error(
                data.error ||
                "Unable to analyze this URL."
            );

        }


        currentData = data.data;


        if (currentData.type === "playlist") {

            showPlaylist(currentData);

        } else {

            showVideo(currentData);

        }


    } catch (error) {

        console.error(error);

        showError(
            cleanError(error.message)
        );

    } finally {

        setLoading(false);

    }

}


// =================================
// Show Video
// =================================

function showVideo(data) {

    resultSection.classList.remove("hidden");


    thumbnail.src =
        data.thumbnail || "";


    videoTitle.textContent =
        data.title || "Untitled video";


    duration.textContent =
        data.duration || "Unknown";


    uploader.textContent =
        data.uploader ||
        data.channel ||
        "Unknown";


    if (data.view_count) {

        videoViews.textContent =
            formatViews(data.view_count);

    } else {

        videoViews.textContent =
            "Views unavailable";

    }


    platformBadge.textContent =
        detectPlatform(data.platform);


    updateQualityOptions(data);


    window.scrollTo({

        top:
            resultSection.offsetTop - 30,

        behavior: "smooth"

    });

}


// =================================
// Quality
// =================================

function updateQualityOptions(data) {

    qualitySelect.innerHTML = "";


    const videos =
        data.formats &&
        data.formats.video
            ? data.formats.video
            : [];


    const qualities = [];


    videos.forEach(format => {

        const height =
            Number(format.height);


        if (
            height &&
            !qualities.includes(height)
        ) {

            qualities.push(height);

        }

    });


    qualities.sort(
        (a, b) => b - a
    );


    if (!qualities.length) {

        const option =
            document.createElement("option");

        option.value = "best";

        option.textContent =
            "Best available";

        qualitySelect.appendChild(option);

        return;
    }


    qualities.forEach(height => {

        const option =
            document.createElement("option");

        option.value =
            height;

        option.textContent =
            `${height}p`;

        qualitySelect.appendChild(option);

    });

}


// =================================
// Format change
// =================================

formatSelect.addEventListener(
    "change",
    function() {

        if (
            formatSelect.value === "mp3"
        ) {

            qualityGroup.classList.add(
                "hidden"
            );

        } else {

            qualityGroup.classList.remove(
                "hidden"
            );

        }

    }
);


// =================================
// Playlist
// =================================

function showPlaylist(data) {

    playlistSection.classList.remove(
        "hidden"
    );


    resultSection.classList.add(
        "hidden"
    );


    document.getElementById(
        "playlistTitle"
    ).textContent =
        data.title || "Playlist";


    document.getElementById(
        "playlistCount"
    ).textContent =
        `${data.count || 0} videos`;


    const container =
        document.getElementById(
            "playlistItems"
        );


    container.innerHTML = "";


    const entries =
        data.entries || [];


    entries.forEach(
        (item, index) => {

            const div =
                document.createElement(
                    "div"
                );

            div.className =
                "playlist-item";


            const img =
                document.createElement(
                    "img"
                );

            img.src =
                item.thumbnail || "";


            img.alt =
                item.title || "Video";


            const title =
                document.createElement(
                    "div"
                );

            title.className =
                "playlist-item-title";


            title.textContent =
                `${index + 1}. ${
                    item.title || "Untitled"
                }`;


            div.appendChild(img);

            div.appendChild(title);

            container.appendChild(div);

        }
    );


    window.scrollTo({

        top:
            playlistSection.offsetTop - 30,

        behavior: "smooth"

    });

}


// =================================
// Prepare Download
// =================================

function prepareDownload() {

    if (!currentData) {

        showError(
            "Analyze a video first."
        );

        return;
    }


    const format =
        formatSelect.value;


    const quality =
        qualitySelect.value;


    /*
       Download endpoint will be added
       in the next phase.
    */


    showError(
        `Download system ready for next phase: ${format.toUpperCase()} ${
            format === "mp4"
                ? quality + "p"
                : ""
        }`
    );

}


// =================================
// Loading
// =================================

function setLoading(status) {

    analyzeBtn.disabled =
        status;


    if (status) {

        analyzeText.classList.add(
            "hidden"
        );

        analyzeLoader.classList.remove(
            "hidden"
        );

    } else {

        analyzeText.classList.remove(
            "hidden"
        );

        analyzeLoader.classList.add(
            "hidden"
        );

    }

}


// =================================
// Errors
// =================================

function showError(message) {

    errorBox.textContent =
        message;

    errorBox.classList.remove(
        "hidden"
    );

}


function hideError() {

    errorBox.classList.add(
        "hidden"
    );

    errorBox.textContent = "";

}


// =================================
// Helpers
// =================================

function formatViews(number) {

    if (number >= 1000000000) {

        return (
            (number / 1000000000)
            .toFixed(1)
        ) + "B views";

    }


    if (number >= 1000000) {

        return (
            (number / 1000000)
            .toFixed(1)
        ) + "M views";

    }


    if (number >= 1000) {

        return (
            (number / 1000)
            .toFixed(1)
        ) + "K views";

    }


    return number + " views";

}


function detectPlatform(platform) {

    if (!platform) {
        return "VIDEO";
    }


    if (
        platform
            .toLowerCase()
            .includes("youtube")
    ) {

        return "YOUTUBE";

    }


    if (
        platform
            .toLowerCase()
            .includes("facebook")
    ) {

        return "FACEBOOK";

    }


    return platform.toUpperCase();

}


function cleanError(message) {

    if (!message) {

        return "Something went wrong.";

    }


    if (
        message
            .toLowerCase()
            .includes("private")
    ) {

        return "This video is private.";

    }


    if (
        message
            .toLowerCase()
            .includes("login required")
    ) {

        return "This video requires login.";

    }


    return message;

}
