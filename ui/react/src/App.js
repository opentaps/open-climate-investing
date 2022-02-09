import "bootstrap/dist/css/bootstrap.min.css";
import React, { Component } from "react";
import { BrowserRouter as Router, Link, Route, Switch } from "react-router-dom";
import "./App.css";
import { SeriesContextProvider } from "./components/series-settings.component";
import StockView from "./components/stock-view.component";
import StocksList from "./components/stocks-list.component";
import BmgAnalysis from "./components/bmg-analysis.component";

class App extends Component {
  getBaseUrl() {
    let baseEl = document.head.querySelector("base");
    if (!baseEl) return "";
    return baseEl.getAttribute("href");
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
              </li><li className="nav-item">
                <Link to={"/bmg-analysis"} className="nav-link">
                  BMG Analysis
                </Link>
              </li>
            </div>
          </nav>

          <div className="main-container container mt-3">
            <SeriesContextProvider>
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
                <Route exact path="/bmg-analysis" component={BmgAnalysis} />
                <Route exact path="/about">
                  <h1>About</h1>
                  <p>The Open Climate Investing about page.</p>
                  <p>
                    See our <Link to={"/terms"}>Terms of Use</Link>
                  </p>
                </Route>
                <Route exact path="/terms">
                  <h1>Terms of Use</h1>
                  <p>
                    Use of this application or website is subject to the{" "}
                    <a
                      href="https://github.com/opentaps/open-climate-investing/blob/main/LICENSE"
                      rel="noreferrer"
                      target="_blank"
                    >
                      License
                    </a>
                    . We specifically do not guarantee the accuracy, completeness,
                    efficiency, timeliness, or correct sequencing of any
                    information. Use of such information is voluntary, and
                    reliance on it should only be undertaken after an independent
                    review of its accuracy, completeness, efficiency, and
                    timeliness. We assume no responsibility for consequences
                    resulting from the use of the information herein, or from use
                    of the information obtained at linked Internet addresses, or
                    in any respect for the content of such information, including
                    (but not limited to ) errors or omissions, the accuracy or
                    reasonableness of factual or scientific assumptions, studies
                    or conclusions, the defamatory nature of statements, ownership
                    of copyright or other intellectual property rights, and the
                    violation of property, privacy, or personal rights of others.
                    We are not responsible for, and expressly disclaims all
                    liability for, damages of any kind arising out of use,
                    reference to, or reliance on such information. No guarantees
                    or warranties, including (but not limited to) any express or
                    implied warranties of merchantability or fitness for a
                    particular use or purpose, are made with respect to such
                    information. At certain places on this application and
                    website, live links to other Internet addresses can be
                    accessed. Such external Internet addresses contain information
                    created, published, maintained, or otherwise posted by
                    institutions or organizations independent of us. We do not
                    endorse, approve, certify, or control these external Internet
                    addresses and does not guarantee the accuracy, completeness,
                    efficacy, timeliness, or correct sequencing of information
                    located at such addresses. Use of information obtained from
                    such addresses is voluntary, and reliance on it should only be
                    undertaken after an independent review of its accuracy,
                    completeness, efficacy, and timeliness. Reference therein to
                    any specific commercial product, process, or service by
                    tradename, trademark, service mark, manufacturer, or otherwise
                    does not constitute or imply endorsement, recommendation, or
                    favoring by us.
                  </p>
                </Route>
              </Switch>
            </SeriesContextProvider>
          </div>
        </div>
        <footer className="bg-light">
          <div className="py-5 container text-left">
             <p>This is part of the open source <a href='https://github.com/opentaps/open-climate-investing' target='_blank' rel="noreferrer">Open Climate Investing</a> project.  See the <a href='https://climate-investing-book.opensourcestrategies.com/v/main/book' target='_blank' rel="noreferrer">free e-book</a> for more information.</p>
             <p>This content is published for informational purposes only and not investment advice or inducement or advertising to purchase or sell any security. See our <Link to={"/terms"}>Terms of Use</Link> and <a href='https://climate-investing-book.opensourcestrategies.com/v/main/book/disclaimer' target='_blank' rel="noreferrer">complete disclaimer.</a></p>
          </div>
        </footer>
      </Router>
    );
  }
}

export default App;
