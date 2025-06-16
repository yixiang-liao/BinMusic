import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';

function BasicExample() {
  return (
    <Navbar expand="lg" className="bg-body-tertiary" bg="light" data-bs-theme="light">
      <Container>
          <Navbar.Brand href="/">
            <img
              alt=""
              src="https://www.bin-music.com.tw/images/logo.png"
            //   width="30"
              height="30"
              className="d-inline-block align-top bin_navbar_img"
            />{'    '}
            相信音樂 大數據分析
          </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link href="/">首頁</Nav.Link>
            <Nav.Link href="/ProjectIntro">專案介紹</Nav.Link>
            <Nav.Link href="/artist">藝人專區</Nav.Link>
            <Nav.Link href="/Album">專輯專區</Nav.Link>
            <Nav.Link href="/News">新聞專區</Nav.Link>
            <Nav.Link href="/LyricFeedback">歌詞互動</Nav.Link>
            <Nav.Link href="/FeedbackList">歌詞回饋</Nav.Link>
            <Nav.Link href="/AIBout">Bin Music LLM</Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default BasicExample;