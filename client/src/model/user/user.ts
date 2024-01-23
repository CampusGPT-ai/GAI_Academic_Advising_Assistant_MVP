export type Demographics = {
    ethnicity: string;
    gender: string;
    academicYear?: string;
  }
  
  export type  Academics = {
    AcademicYear?: string;
    Major: string;
    Minor?: string;
  }
  
  export type  UserProfile = {
    _id: string;
    user_id: string;
    institution: string;
    full_name: string;
    avatar: string;  //https://picsum.photos/80/80
    interests: string[];
    demographics: Demographics;
    academics: Academics;
    courses?: string[];
  }
  