const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
require("dotenv").config();

const app = express();

var corsOptions = {
  origin: "*",
};

app.use(cors(corsOptions));

// parse requests of content-type - application/json
app.use(bodyParser.json());

// parse requests of content-type - application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: true }));

// to use sequelize to generate the models ? but we already have a schema script
// so disable this for now ..
//const db = require("./app/models");
//db.sequelize.sync();

// simple route
app.get("/api/", (req, res) => {
  res.json({ message: "Open Climate Investing." });
});

require("./app/routes/stock.routes")(app);
require("./app/routes/stock_components.routes")(app);
require("./app/routes/stock_parents.routes")(app);
require("./app/routes/stock_data.routes")(app);
require("./app/routes/stock_stats.routes")(app);
require("./app/routes/stock_factor_names.routes")(app);

// set port, listen for requests
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}.`);
});
