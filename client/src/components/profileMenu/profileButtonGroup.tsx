import { Box } from "@mui/material";
import React, { FC, useEffect, useState } from "react";
import ProfileButtonComponent from "./profileButton";

/**
 * Props for the ButtonGroup component.
 */
interface ButtonGroupProps {
  /**
   * An array of strings representing the list of buttons to be rendered.
   */
  buttonList: string[];
  /**
   * A function that acts on the selected values of the button group.
   * @param list - An array of strings representing the selected values.
   */
  handleSelectedValues: (list: string[]) => void;
}

const ButtonGroupComponent: FC<ButtonGroupProps> = ({
  buttonList,
  handleSelectedValues,
}) => {
  const [selectedList, setSelectedList] = useState<string[]>([]);

  /**
   * Sets the selected value based on the button value and whether it is selected or not.
   * @param buttonValue - The value of the button that was clicked.
   * @param isSelected - Whether the button was selected or deselected.
   */
  const setSelectedValueHandler = (
    buttonValue: string,
    isSelected: boolean
  ) => {
    let updatedList;
    if (isSelected) {
      updatedList = [...selectedList, buttonValue];
    } else {
      updatedList = selectedList.filter((value) => value !== buttonValue);
    }
    setSelectedList(updatedList);
    handleSelectedValues(updatedList);
  };

  
  useEffect(() => {
    // Filter out the selected values that are no longer in buttonList,
    // as button list changes when interests change
    const updatedSelectedList = selectedList.filter(value => buttonList.includes(value));
    setSelectedList(updatedSelectedList);
    handleSelectedValues(updatedSelectedList);
  }, [buttonList]);


  return (
    <Box
      sx={{
        m: 2,
        display: "flex",
        flexDirection: "row",
        flexWrap: "wrap",
        width: "100%", 
      }}
    >
      {buttonList.map((string, index) => (
        <ProfileButtonComponent
          key={index}
          buttonValue={string}
          onButtonClick={setSelectedValueHandler}
        />
      ))}
    </Box>
  );
};

ButtonGroupComponent.defaultProps = {
  buttonList: ["string1", "string2", "string3", "string4", "string5"],
  handleSelectedValues: (list: string[]) => {
    console.log("button clicked");
  },
};

export default ButtonGroupComponent;
