namespace AccessorCase
{
	// order determines priority
	Enum 
	{
		None,
		BaseData,
		SparseData,
		BaseDataWithOverrides,
		SparseDataWithMutator,
		BaseDataWithOverridesAndMutator,
		DirectData,
	}
}
struct ConfigArraySettings
{
	ConfigArraySettings(): bCacheData(false), eAccessor(None) {}
	Bool bCacheData;
	AccessorCase::Enum eAccessor;
}
template<VALUE>
class ConfigArray
{
	CheckedPtr<ConfigArray> m_pBaseData;
	ManagedPtr<Vector<VALUE>> m_pvData;
	ManagedPtr<OrderedMap<UInt, VALUE>> m_pvSparseData;
	ManagedPtr<Delegate<VALUE (UInt, VALUE)>> m_pfMutator;
	
	ConfigArraySettings m_Settings;
	
	Bool PostLoad()
	{
		Map<AccessorCase::Enum, Bool> accessors;
		accessors[AccessorCase::DirectData] = (m_pvData != NULL);
		accessors[AccessorCase::BaseData] = (m_pBaseData != NULL);
		accessors[AccessorCase::BaseDataWithOverrides] = accessors[AccessorCase::BaseData] && (m_pvSparseData != NULL);
		accessors[AccessorCase::BaseDataWithOverridesAndMutator] = accessors[AccessorCase::BaseDataWithOverrides] && (m_pfMutator != NULL);
		accessors[AccessorCase::SparseData] = (m_pvSparseData != NULL);
		accessors[AccessorCase::SparseDataWithMutator] = accessors[AccessorCase::SparseData] && (m_pfMutator != NULL);
		
		UInt uPotentialAccessors = accessors.Sum( x => x ? 1 : 0 );
		if (accessors[AccessorCase::DirectData])
		{
			if(uPotentialAccessors != 1)
			{
				return false;
			}
		}
		else
		{
			if (uPotentialAccessors < 1)
			{
				return false;
			}
		}
		
		AccessorCase::Enum eAccessor;
		for (auto pair : accessors)
		{
			if (pair.Second && pair.First > eAccessor)
			{
				eAccessor == pair.First;
			}
		}
		
		if (!m_Settings.bCacheData)
		{
			m_Settings.eAccessor = eAccessor;
			return true;
		}
		m_Settings.eAccessor = AccessorCase::DirectData;
		if (eAccessor == AccessorCase::SparseData || eAccessor == AccessorCase::SparseDataWithMutator)
		{
			UInt uPreviousIndex = 0;
			for (auto iter : m_vSparseData)
			{
				VALUE value = iter.Second;
				if (eAccessor == AccessorCase::SparseDataWithMutator)
				{
					value = m_pfMutator(iter.First, value);
				}
				m_pvData->Insert(uPreviousIndex + 1, iter.First, value);
				uPreviousIndex = iter.First;
			}
			return true;
		}
		
		for (auto iter : m_pBaseData)
		{
			VALUE value = iter.Second;
			if (accessors[AccessorCase::SparseData])
			{
				if (m_pvSparseData.HasValue(iter.First))
				{
					value = m_pvSparseData.GetValue(iter.First);
				}
			}
			if (eAccessor == AccessorCase::BaseDataWithOverridesAndMutator)
			{
				value = m_pfMutator(iter.First, value);
			}
			m_pvData->PushBack(value);
		}
		if (accessors[AccessorCase::SparseData])
		{
			UInt uBaseDataSize = m_pvData.GetSize();
			if (m_pvSparseData.Back().First >= uBaseDataSize)
			{
				UInt uPreviousIndex = uBaseDataSize;
				for (auto iter : m_vSparseData)
				{
					if (iter.First < uBaseDataSize)
					{
						continue;
					}
					VALUE value = iter.Second;
					if (eAccessor == AccessorCase::BaseDataWithOverridesAndMutator)
					{
						value = m_pfMutator(iter.First, value);
					}
					m_pvData->Insert(uPreviousIndex + 1, iter.First, value);
					uPreviousIndex = iter.First;
				}
			}
		}
		return true;
	}
}
