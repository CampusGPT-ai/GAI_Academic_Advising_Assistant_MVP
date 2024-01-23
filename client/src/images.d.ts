// images.d.ts

declare module "*.png" {
    const value: any;
    export = value;
}

declare module "*.jpg" {
    const value: any;
    export = value;
}

// You can also add similar declarations for other file types if needed
// e.g., jpg, jpeg, svg, etc.
