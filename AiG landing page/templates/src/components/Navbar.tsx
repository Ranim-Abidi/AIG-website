import { useState } from 'react'
import { Link } from 'react-router-dom'
import whiteBlueLogo from '/White-Blue-Logo.png'
import './FormComponents.css'

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  const closeMenu = () => {
    setIsMenuOpen(false)
    setIsDropdownOpen(false)
  }

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="logo">
          <Link to="/" onClick={closeMenu}>
            <img src={whiteBlueLogo} alt="AIESEC" className="logo-img" />
          </Link>
        </div>

        <button
          type="button"
          className={`menu-toggle ${isMenuOpen ? 'active' : ''}`}
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-label="Toggle navigation menu"
          aria-expanded={isMenuOpen}
        >
          <div className="bar"></div>
          <div className="bar"></div>
          <div className="bar"></div>
        </button>

        <ul className={`nav-links ${isMenuOpen ? 'active' : ''}`}>
          <li>
            <Link to="/" onClick={closeMenu}>Home</Link>
          </li>
          <li className={`dropdown ${isDropdownOpen ? 'active' : ''}`}>
            <Link
              to="/#products"
              onClick={(e) => {
                if (isMenuOpen) {
                  e.preventDefault()
                  setIsDropdownOpen(!isDropdownOpen)
                } else {
                  closeMenu()
                }
              }}
            >
              Our Products
              {isMenuOpen && (
                <span className="dropdown-chevron">
                  {isDropdownOpen ? '▲' : '▼'}
                </span>
              )}
            </Link>
            <div className="dropdown-menu">
              <Link to="/global-volunteer" className="dropdown-item" onClick={closeMenu}>
                Global Volunteer
              </Link>
              <Link to="/global-talent" className="dropdown-item" onClick={closeMenu}>
                Global Talent
              </Link>
              <Link to="/global-teacher" className="dropdown-item" onClick={closeMenu}>
                Global Teacher
              </Link>
              <Link to="/member" className="dropdown-item" onClick={closeMenu}>
                AIESEC Member
              </Link>
            </div>
          </li>
        </ul>
      </div>
    </nav>
  )
}
