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
      console.log("** retrieveFrequencies **", this.props);
      const { data: frequencies } = await StockDataService.getFrequencies({ ticker: this.props.ticker });
      if (!frequencies.find(e=>{
        if (e.frequency == this.context.frequency) return true;
        if (this.context.frequency.indexOf("(") != 0 && e.frequency.indexOf("(") == 0) {
          // also set it to the value including the interval
          if (e.frequency.substring(1, e.frequency.length-1).split(",")[0] == this.context.frequency) {
            this.context.setFrequency(e.frequency);
            return true;
          }
        } else if (this.context.frequency.indexOf("(") == 0 && e.frequency.indexOf("(") != 0) {
          // reverse, consider the value without the interval
          if (this.context.frequency.substring(1, this.context.frequency.length-1).split(",")[0] == e.frequency) {
            this.context.setFrequency(e.frequency);
            return true;
          }
        }
        return false;
      })) {
        console.log("** retrieveFrequencies setting frequency from / to", this.context.frequency, frequencies[0].frequency);
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

    return ((factorNames && factorNames.length) || (frequencies && frequencies.length)) ? (
      <div className="col-12 ms-1 mb-2 d-flex flex-row align-items-baseline">
        {(factorNames && factorNames.length) ? (
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
        ):''}
        {(frequencies && frequencies.length) ? (
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
        ):''}
      </div>
    ):''
  }
}

SeriesSettings.contextType = SeriesContext;

SeriesSettings.propTypes = {
  ticker: PropTypes.string
}

export default SeriesSettings;

