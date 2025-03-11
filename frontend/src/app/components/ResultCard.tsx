import { Film } from '@/app/types/Film'

export const ResultCard = ({ films }: { films: Film[] }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full px-2 sm:px-0">
            {films.map((film, index) => (
            <div key={index} className="bg-white dark:bg-gray-700 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 w-full border border-gray-200 dark:border-gray-700">
                <div className="p-3 sm:p-3 sm:pl-6 sm:pr-6 flex flex-col sm:flex-row items-start sm:items-top justify-between">
                    <div className="w-full sm:w-auto mb-2 sm:mb-0">
                        <h3 className="text-l font-bold text-gray-800 dark:text-white mb-1 break-words">{film.title}</h3>
                        <div className="text-sm text-gray-600 dark:text-gray-300 mb-0">{film.date}</div>
                        <div className="text-sm text-indigo-300 dark:text-indigo-300 mb-0">{film.note}</div>
                    </div>
                    <div className="flex w-full flex-row sm:flex-col gap-2 flex-wrap mt-2 sm:mt-0">
                        <div className="flex w-full gap-2 justify-end items-end flex-col sm:items-end">
                            {film.providers.map((provider, index) => (
                                <span key={index} className="px-3 py-1 text-xs rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 font-medium">
                                {provider}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
            ))}
        </div>
    )
}
