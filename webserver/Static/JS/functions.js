var OSName = "Unknown";
function getOS() {
    if (window.navigator.userAgent.indexOf("Windows NT 10.0")!= -1) return "Windows";
    if (window.navigator.userAgent.indexOf("Windows NT 6.2") != -1) return "Windows";
    if (window.navigator.userAgent.indexOf("Windows NT 6.1") != -1) return "Windows";
    if (window.navigator.userAgent.indexOf("Windows NT 6.0") != -1) return "Windows";
    if (window.navigator.userAgent.indexOf("Windows NT 5.1") != -1) return "Windows XP";
    if (window.navigator.userAgent.indexOf("Windows NT 5.0") != -1) return "Windows 2000";
    if (window.navigator.userAgent.indexOf("Mac")            != -1) {
        if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
            return "Mobile"
        }
        return "Mac"
    };
    if (window.navigator.userAgent.indexOf("X11")            != -1) return "UNIX";
    if (window.navigator.userAgent.indexOf("Linux")          != -1) return "Linux";
}
OSName = getOS()

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

