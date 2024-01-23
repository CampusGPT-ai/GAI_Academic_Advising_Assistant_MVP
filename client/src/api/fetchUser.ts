import { UserProfile } from '../model/user/user';
import { BaseUrl } from "./baseURL";

interface fetchUsersParams {
  institution: string;
}

const fetchUsers = async ({
  institution,
}: fetchUsersParams): Promise<UserProfile[]> => {
  const apiUrl = `${BaseUrl()}/institutions/${institution}/users`;
  try {
    return [];
   
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export default fetchUsers;
