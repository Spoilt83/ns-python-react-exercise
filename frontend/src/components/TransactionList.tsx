import React, { useEffect, useState } from 'react';

interface Transaction {
  id: number;
  description: string;
  amount: number;
  type: string;
  category_rel: {
    id: number;
    name: string;
  };
  date: string;
  user_id: number;
}

const TransactionList: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const pageSize = 10;

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/v1/transactions/?limit=1000');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: Transaction[] = await response.json();
        setTransactions(data);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, []);

  const filteredTransactions = transactions.filter(transaction => {
    if (filterType === 'all') return true;
    return transaction.type === filterType;
  });

  const totalPages = Math.ceil(filteredTransactions.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedTransactions = filteredTransactions.slice(startIndex, endIndex);

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterType(e.target.value);
    setCurrentPage(1); // Reset to first page when filter changes
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  if (loading) {
    return <div className="text-gray-700">Loading transactions...</div>;
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg mt-8">
      <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Transactions</h3>
        <div className="flex items-center gap-2">
          <label htmlFor="type-filter" className="text-sm font-medium text-gray-700">
            Filter by type:
          </label>
          <select
            id="type-filter"
            value={filterType}
            onChange={handleFilterChange}
            className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All</option>
            <option value="credit">Credit</option>
            <option value="debit">Debit</option>
          </select>
        </div>
      </div>
      <div className="border-t border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-[15%]">Date</th>
              <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-[10%]">Type</th>
              <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-[20%]">Category</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[35%]">Description</th>
              <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-[20%]">Amount</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedTransactions.map((transaction, index) => (
              <tr key={transaction.id} className={`${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}`}>
                <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-500">
                  {new Date(transaction.date).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className={`px-2 inline-flex justify-center text-center text-xs leading-5 font-semibold rounded-full ${
                    transaction.type === 'credit' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {transaction.type}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-500">
                  {transaction.category_rel.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-left text-sm font-medium text-gray-900">
                  {transaction.description}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-900">
                  ${transaction.amount.toFixed(2)}
                </td>
              </tr>
            ))}
            {paginatedTransactions.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center text-gray-500">No transactions found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 sm:px-6 flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Page {currentPage} of {totalPages} ({filteredTransactions.length} transactions)
          </div>
          <div className="flex gap-2">
            <button
              onClick={handlePreviousPage}
              disabled={currentPage === 1}
              className={`px-3 py-1 rounded text-sm font-medium ${
                currentPage === 1
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-500 text-white hover:bg-blue-600'
              }`}
            >
              Previous
            </button>
            <button
              onClick={handleNextPage}
              disabled={currentPage === totalPages}
              className={`px-3 py-1 rounded text-sm font-medium ${
                currentPage === totalPages
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-500 text-white hover:bg-blue-600'
              }`}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TransactionList;
