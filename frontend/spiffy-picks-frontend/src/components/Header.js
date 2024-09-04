import React from 'react';
import './Header.css';

const Header = () => {
    return (
        <header>
            <div className="logo">SpiffyPicks</div>
            <nav>
                <ul>
                    <li><a href="/top-picks">Top Picks</a></li>
                    <li><a href="/all-picks">All Picks</a></li>
                </ul>
            </nav>
        </header>
    );
};

export default Header;