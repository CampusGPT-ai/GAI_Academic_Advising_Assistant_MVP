import { UserProfile } from "../model/user/user";
import userSample from '../model/user/userSample.json';

const jsonString = JSON.stringify(userSample);
const usersimport = JSON.parse(jsonString) as UserProfile[];

const getUserProfile = (user_id: string): UserProfile => {

    // Find the user in the users array whose user_id matches the provided user_id
    try{
        const user = usersimport.find(user => user.user_id === user_id);
        if (user != undefined)
        {return user;}
        else {throw Error("user not found")}
    }
    catch (error) {
        throw(error)
    }
    
    // If a matching user is found, return the user profile, otherwise return null
    
}

export default getUserProfile;