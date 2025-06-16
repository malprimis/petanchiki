import { Link, useLocation, useParams } from 'react-router-dom';

const Breadcrumbs = () => {
  const location = useLocation();
  const params = useParams();
  
  const pathnames = location.pathname.split('/').filter(x => x);
  const pathTitles: Record<string, string> = {
    'group': 'Группа',
    'reports': 'Отчеты',
    'add-transaction': 'Добавить транзакци'
  };

  return (
    <div className="bg-gray-100">
      <div className="container mx-auto px-4 py-2 text-sm text-gray-600">
        <Link to="/" className="hover:text-blue-500"></Link>
        {pathnames.map((path, index) => {
          const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`;
          const isLast = index === pathnames.length - 1;
          const title = pathTitles[path] || path;
          
          return (
            <span key={path}>
              <span className="mx-2">→</span>
              {isLast ? (
                <span>{path in params ? `${title} ${params[path]}` : title}</span>
              ) : (
                <Link to={routeTo} className="hover:text-blue-500">
                  {title}
                </Link>
              )}
            </span>
          );
        })}
      </div>
    </div>
  );
};

export default Breadcrumbs;