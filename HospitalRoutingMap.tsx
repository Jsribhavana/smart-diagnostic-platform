import React from 'react';
import { Hospital } from '../types/hospital';

interface HospitalRoutingMapSimpleProps {
    selectedHospital?: Hospital;
    onHospitalSelect?: (hospital: Hospital) => void;
}

const HospitalRoutingMapSimple: React.FC<HospitalRoutingMapSimpleProps> = ({
    selectedHospital,
    onHospitalSelect
}) => {
    return (
        <div>
            <h2>Map Component</h2>
            <p>This is a simple test component</p>
            <p>Selected Hospital: {selectedHospital?.name || 'None'}</p>
        </div>
    );
};

export default HospitalRoutingMapSimple;
