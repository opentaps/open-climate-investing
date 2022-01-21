import PropTypes from 'prop-types';
import React, { Component, useState } from "react";
import StockDataService from "../services/stock.service";
import { FormControl, MenuItem, Select } from "@mui/material";

export const DEFAULT_FACTOR_NAME = "DEFAULT";
export const DEFAULT_FREQUENCY = "MONTHLY";


export const SeriesContext = React.createContext({
  frequency: DEFAULT_FREQUENCY,
  factorName: DEFAULT_FACTOR_NAME,
  setFactorName: (value) => console.log('Set factor name to ', value),
  setFrequency: (value) => console.log('Set frequency to ', value),
});

export const SeriesContextProvider = ({ children }) => {
  const [factorName, setFactorName] = useState(DEFAULT_FACTOR_NAME);
  const [frequency, setFrequency] = useState(DEFAULT_FREQUENCY);

  return (
    <SeriesContext.Provider value={{
      frequency,
      factorName,
      setFactorName,
      setFrequency
    }}>
      {children}
    </SeriesContext.Provider>
  )
}

SeriesContextProvider.propTypes = {
  children: PropTypes.object
}


class SeriesSettings extends Component {
  constructor(props) {
    super(props);
    this.handleFactorNameChange = this.handleFactorNameChange.bind(this);
    this.handleFrequencyChange = this.handleFrequencyChange.bind(this);

    this.state = {
      frequencies: [],
      factorNames: [],
    }
  }

  componentDidMount() {
    this.retrieveFrequencies();
    this.retrieveFactorNames();
  }

  async retrieveFrequencies() {
    try {
      const { data: frequencies } = await StockDataService.getFrequencies();
      if (!frequencies.find(e=>e.frequency == this.context.frequency)) {
        this.context.setFrequency(frequencies[0].frequency);
      }
      this.setState({
        frequencies: frequencies.map((e) => e.frequency),
      });
    } catch (err) {
      console.log(err);
    }
  }

  async retrieveFactorNames() {
    try {
      const { data: factor_names } = await StockDataService.getFactorNames();
      if (!factor_names.find(e=>e.factor_name == this.context.factorName)) {
        this.context.setFactorName(factor_names[0].factor_name);
      }
      this.setState({
        factorNames: factor_names.map((e) => e.factor_name),
      });
    } catch (err) {
      console.log(err);
    }
  }

  handleFrequencyChange(event) {
    let value = event.target.value;
    console.log("handleFrequencyChange:: ", event, value);
    this.context.setFrequency(value);
  }

  handleFactorNameChange(event) {
    let value = event.target.value;
    console.log("handleFactorNameChange:: ", event, value);
    this.context.setFactorName(value);
  }

  render() {
    const { factorNames, frequencies } = this.state;
    const { factorName, frequency } = this.context;

    return ((factorNames && factorNames.length) || (frequencies && frequencies.length)) && (
      <div className="col-12 ms-1 mb-2 d-flex flex-row align-items-baseline">
        {factorNames && factorNames.length && (
          <div className="ms-1 mb-2 d-flex flex-row align-items-baseline">
            <b className="me-2">BMG Factor</b>
            <FormControl variant="standard">
              <Select
                value={factorName}
                onChange={this.handleFactorNameChange}
              >
                {factorNames.map((fname) => (
                  <MenuItem key={fname} value={fname}>
                    {fname}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </div>
        )}
        {frequencies && frequencies.length && (
          <div className="ms-1 mb-2 d-flex flex-row align-items-baseline">
            <b className="me-2">Frequency</b>
            <FormControl variant="standard">
              <Select
                value={frequency}
                onChange={this.handleFrequencyChange}
              >
                {frequencies.map((fname) => (
                  <MenuItem key={fname} value={fname}>
                    {fname}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </div>
        )}
      </div>
    )
  }
}

SeriesSettings.contextType = SeriesContext;

export default SeriesSettings;

