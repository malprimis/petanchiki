import { Link, useLocation } from 'react-router-dom';

const Header = () => {
  const location = useLocation();
  
  return (
    <header className="bg-blue-600 text-white p-4 shadow-md">
      <nav className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-xl font-bold"></Link>
        <div className="flex space-x-6">
          <Link 
            to="/" 
            className={`hover:underline ${location.pathname === '/' ? 'font-bold underline' : ''}`}
          >
            
          </Link>
          <Link 
            to="/reports" 
            className={`hover:underline ${location.pathname === '/reports' ? 'font-bold underline' : ''}`}
          >
            
          </Link>
        </div>
      </nav>
    </header>
  );
};

export default Header;