import { FC } from 'react';
import logo from '../../../assets/images/ucflogo.png';
interface LogoProps {
    size: string;
}

const Logo: FC<LogoProps> = ({ size }) => { 
    var height = "60px";
    var width = "60px";

    switch (size) {
        case "large":
            height = "140px";
            width = "140px";
            break;
        case "medium":
            height = "100px";
            width = "100px";
            break;
        default:
            break;
    }

    return (
        <img src={logo} height={height} width={width} alt="Logo" />
    );
}

Logo.defaultProps = {
    size: "small",
}

export default Logo;
