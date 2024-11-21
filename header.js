class Header extends HTMLElement {
    constructor() {
        super();

        this.innerHTML = `
        <header style="padding: 20px 0;">
            <div class="container" style="margin-bottom: 40px;">
                <div class="header" style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 20px;">
                    <!-- Emosync Logo -->
                    <span class="logo">
                        <a href="${homeUrl}">
                            <img src="/static/images/logosymbol.png" alt="Your Logo" style="height: 200px; width: auto; margin-bottom: 0;"/>
                        </a>
                    </span>

                    <!-- Home Button with increased margin-top -->
                    <span class="home-button" style="margin-left: auto; display: flex; align-items: center; margin-top: 60px;">
                        <a href="${homeUrl}" style="text-decoration: none; color: inherit;">
                            <img src="/static/images/home_icon.png" alt="Home" style="height: 45px; width: auto; margin-right: 10px;"/>
                        </a>
                    </span>

                    <!-- User Page Button -->
                    <span class="user-page-button" style="margin-left: 20px; display: flex; align-items: center; margin-top: 60px;">
                        <a href="/user" style="text-decoration: none; color: inherit;">
                            <img src="/static/images/user.png" alt="User Page" style="height: 45px; width: auto; margin-right: 10px;"/>
                        </a>
                    </span>
                </div>
                
                <!-- Adjusted margin to avoid overlap -->
                <div id="mySidenav" class="sidenav" style="margin-top: 40px;">
                    <span class="sidenav-logo">
                        <a href="${homeUrl}">
                            <img src="/static/images/header.png" alt="Your Logo" style="height: 100px; width: auto;"/>
                        </a>
                    </span>
                </div>
            </div>
        </header>
        `;
    }
}

window.customElements.define('custom-header', Header);
