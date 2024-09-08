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
                    <li><a href="/top-props">Top Props</a></li>
                    <li><a href="/all-props">All Props</a></li>
                    <li><a href="/parlays">Parlays</a></li>
                </ul>
            </nav>
        </header>
    );
};

export default Header;