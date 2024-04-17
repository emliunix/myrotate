import React, { useState, useEffect } from 'react';
import "./AngleDisplay.css";

function AngleDisplay() {
    const [angle, setAngle] = useState(0);

    useEffect(() => {
        const eventSource = new EventSource('/api/data/rotary');
        eventSource.addEventListener("data", (event) => {
            const newAngle = JSON.parse(event.data).angle;
            console.log(newAngle);
            setAngle(newAngle);
        });

        return () => {
            eventSource.close();
        };
    }, []);

    return (
        <div className="plate">
            <div className="pointer" style={{ transform: `translateX(50%) rotate(${angle}deg)` }} />
        </div>
    );
};

export default AngleDisplay;