import { Button } from '@mui/material';
import { FC, useState } from 'react';


/**
 * Props for the ProfileButton component.
 */
/**
 * Props for the ProfileButton component.
 */
interface ProfileButtonProps {
    /**
     * The value of the button.
     */
    buttonValue: string;
    /**
     * Function to be called when the button is clicked.
     * @param buttonValue - The value of the button.
     * @param isSelected - Whether the button is currently selected.
     */
    onButtonClick: (buttonValue: string, isSelected: boolean) => void;
}

const ProfileButtonComponent: FC<ProfileButtonProps> = ({buttonValue, onButtonClick}) => {
    const [selected, setSelected] = useState(false);

  const handleButtonClick = (buttonText: string) => {
    setSelected(!selected);
    onButtonClick(buttonValue, !selected);
  };

  return (
   
    <Button 
      onClick={() => handleButtonClick(buttonValue)}
      sx={(theme) => ({
          backgroundColor: selected ? theme.palette.primary.main : theme.palette.secondary.main,
            color: selected ? theme.palette.primary.contrastText : theme.palette.primary.contrastText,
            m: 1,
            p:1
        })}>
        {buttonValue}
    </Button>
  );
};


ProfileButtonComponent.defaultProps = {
    buttonValue: "string1",
    onButtonClick: (buttonValue: string, isSelected: boolean) => {console.log("button clicked")},
  

}

export default ProfileButtonComponent;
