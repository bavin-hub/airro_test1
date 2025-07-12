import {Link} from 'react-router-dom'
function Navbar(){

    return(
        <nav className="nav">
            <Link to="/" className="site-title">
                AIRRO
            </Link>
            <ul>
                <li className="active">
                    <Link to="/home">Home</Link>
                </li>
                <li>
                    <Link to="/models">Models</Link>
                </li>
            </ul>
        </nav>
    )
}


export default Navbar