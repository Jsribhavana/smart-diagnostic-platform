import React from 'react';
import { Navbar, Nav, Container } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useTranslation } from '../i18n';
import LanguageSelector from './LanguageSelector';

const Header: React.FC = () => {
  const { t } = useTranslation();
  return (
    <Navbar bg="primary" variant="dark" expand="lg" sticky="top">
      <Container>
        <Navbar.Brand as={Link} to="/">{t('header.brand')}</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto align-items-center">
            <Nav.Link as={Link} to="/">{t('header.nav.home')}</Nav.Link>
            <Nav.Link as={Link} to="/nearby-centers">{t('header.nav.nearby_centers')}</Nav.Link>
            <Nav.Link as={Link} to="/test-analysis">{t('header.nav.test_analysis')}</Nav.Link>
            <Nav.Link as={Link} to="/food-products">{t('header.nav.food_products')}</Nav.Link>
            <Nav.Link as={Link} to="/medicines">{t('header.nav.medicines')}</Nav.Link>
            <Nav.Link as={Link} to="/test-prices">{t('header.nav.test_prices')}</Nav.Link>
            <Nav.Link as={Link} to="/hospital-routing">Hospital Routing</Nav.Link>
            <div className="ms-3">
              <LanguageSelector />
            </div>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Header;