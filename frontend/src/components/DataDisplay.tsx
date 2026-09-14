import React, {type FC} from "react";
import type { AllergenPresence, NutritionalValue as NutritionalValue } from "@/types";
import {X, Check, AlertTriangle, BarChart} from './Icons';



const AllergenItem: FC<{ item: AllergenPresence }> = ({ item }) => (
  <li className="flex justify-between items-start p-3 border-b border-gray-700 last:border-b-0 hover:bg-gray-700/50 transition-colors">
    <span className="font-medium text-gray-200">{item.allergen}</span>
    <div className="flex flex-col items-end">
      <span className={`font-bold flex items-center text-sm ${item.present ? 'text-red-400' : 'text-green-400'}`}>
        {item.present ? <X size={16} className="mr-1" /> : <Check size={16} className="mr-1" />}
        {item.present ? 'TALÁLT' : 'NEM TALÁLT'}
      </span>
      {item.notes && <span className="text-xs mt-1 text-gray-400 text-right">{item.notes}</span>}
    </div>
  </li>
);


export const AllergensDisplay: FC<{ allergens: AllergenPresence[] }> = ({ allergens }) => (
  <div className="bg-gray-800 rounded-xl p-4 shadow-xl border border-gray-700">
    <h3 className="text-xl font-semibold mb-3 flex items-center text-red-300">
      <AlertTriangle size={20} className="mr-2" /> Allergének ellenőrzése
    </h3>
    <ul className="divide-y divide-gray-700 max-h-80 overflow-y-auto">
      {allergens?.length > 0 ? (
        allergens.map((item, index) => <AllergenItem key={index} item={item} />)
      ) : (
        <p className="text-gray-400 p-2">Nem található allergén adatok</p>
      )}
    </ul>
  </div>
);

export const NutritionalValuesDisplay: FC<{ nutritionalValues: NutritionalValue[] }> = ({ nutritionalValues }) => (
  <div className="bg-gray-800 rounded-xl p-4 shadow-xl border border-gray-700">
    <h3 className="text-xl font-semibold mb-3 flex items-center text-blue-300">
      <BarChart size={20} className="mr-2" /> Tápanyagok
    </h3>
    <div className="grid grid-cols-2 text-sm font-medium border-b border-gray-600 pb-1 mb-2 text-gray-400">
      <span className="p-2">Tápanyag</span>
      <span className="p-2 text-right">Mennyiség</span>
    </div>
    <div className="max-h-80 overflow-y-auto">
      {nutritionalValues.length > 0 ? (
        nutritionalValues.map((item, index) => (
          <div key={index} className="grid grid-cols-2 border-b border-gray-700 last:border-b-0 hover:bg-gray-700/50 transition-colors">
            <span className="p-2 text-gray-200">{item.nutrient}</span>
            {}
            <span className="p-2 text-right font-bold text-gray-100">{item.amount || 'N/A'}</span>
          </div>
        ))
      ) : (
        <p className="text-gray-400 p-2">Nem találhatók tápanyag értékek.</p>
      )}
    </div>
  </div>
);