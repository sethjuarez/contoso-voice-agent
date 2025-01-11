import { WEB_ENDPOINT } from "@/store/endpoint";

interface Claim {
  provider_name: string;
  user_claims: {
    typ: string;
    val: string;
  }[];
  user_id: string;
  [key: string]: unknown;
}
const defaultUser: Claim[] = [
  {
    provider_name: "aad",
    user_claims: [
      {
        typ: "name",
        val: "Isaac Juarez",
      },
      {
        typ: "preferred_username",
        val: "sejuare@microsoft.com",
      },
    ],
    user_id: "Seth.Juarez@microsoft.com",
    other: "sdsd",
  },
];

export interface User {
  name: string;
  email: string;
  image?: string;
}

const checkUrlStatus = async (url: string): Promise<boolean> => {
  try {
    const response = await fetch(url);
    return response.ok && response.status === 200;
  } catch  {
    return false;
  }
};

export const fetchUser = async (): Promise<User> => {
  let u: Claim[] = defaultUser;
  try {
    const response = await fetch(`${WEB_ENDPOINT}/.auth/me`);
    if (response.ok) {
      console.log("using easyauth user")
      u = await response.json();
    }
  } catch {
    // ignore
    console.log("Error fetching user");
  }

  const name =
    u[0].user_claims.find((c) => c.typ === "name")?.val || "Seth Juarez";
  const email = u[0].user_id;
  const image = `${WEB_ENDPOINT}/people/${name
    .toLowerCase()
    .replace(" ", "-")}.jpg`;
  if (await checkUrlStatus(image)) {
    return { name, email, image };
  } else {
    return { name, email };
  }
};
