import "bootstrap/dist/css/bootstrap.min.css";
import React, { Component } from "react";
import { BrowserRouter as Router, Link, Route, Switch } from "react-router-dom";
import "./App.css";
import StockView from "./components/stock-view.component";
import StocksList from "./components/stocks-list.component";

class App extends Component {
  getBaseUrl() {
    let baseEl = document.head.querySelector("base");
    if (!baseEl) return "";
    return baseEl.getAttribute("href");
  }

  render_term_link() {
    const termUrl =
      "https://github.com/opentaps/open-climate-investing/blob/main/LICENSE";
    return (
      <a target="_blank" href={termUrl}>
        Terms of Use
      </a>
    );
  }

  render() {
    const basename = this.getBaseUrl();
    return (
      <Router basename={basename}>
        <div>
          <nav className="navbar navbar-expand navbar-dark bg-dark">
            <Link to={"/stocks"} className="navbar-brand">
              Open Climate Investing
            </Link>
            <div className="navbar-nav mr-auto">
              <li className="nav-item">
                <Link to={"/stocks"} className="nav-link">
                  Stocks
                </Link>
              </li>
            </div>
          </nav>

          <div className="container mt-3">
            <Switch>
              <Route
                exact
                path={[
                  "/",
                  "/stocks",
                  "/stocks-list",
                  "/stocks-list/:pageSize",
                  "/stocks-list/:pageSize/:page",
                  "/stocks-list/:pageSize/:page/:filters*",
                ]}
                component={StocksList}
              />
              <Route exact path="/stocks/:id" component={StockView} />
              <Route exact path="/about">
                <h1>About</h1>
                <p>The Open Climate Investing about page.</p>
                <p>See our {this.render_term_link()}</p>
              </Route>
              <Route exact path="/terms">
                <h1>Terms of Use</h1>
                <p>See our {this.render_term_link()}</p>
              </Route>
            </Switch>
          </div>
        </div>
        <footer className="bg-light">
          <div className="py-5 container text-left">
            <p>See our {this.render_term_link()}</p>
          </div>
        </footer>
      </Router>
    );
  }
}

export default App;
