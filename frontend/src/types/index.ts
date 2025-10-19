export type NutritionalValue = {
    nutrient: string;
    amount: string|null;
    notes: string|null;
};

export type AllergenPresence = {
    allergen: string;
    present: boolean;
    notes: string | null;
};

export type ExtractionResult = {
    productName: string;
    nutritionalValues: NutritionalValue[];
    allergens: AllergenPresence[];
    language: string;
};

export type Status = 'idle'|'loading'|'success'|'error'