from math import log
MISSINGCHAR = '?'
STOPPING_INDEX = 7  # 7 or 19 the species name: stop splitting
NUMERICAL = [2, 4]  # 2,4 or 5,7
NUMBER_RANGE = []

class decisionnode:
  def __init__(self,col=-1,value=None,results=None,tb=None,fb=None):
    self.col=col
    self.value=value
    self.results=results
    self.tb=tb
    self.fb=fb

def get_prohibited_traits(binstring):
    prohibited_traits = [5, 6, 17]

    if binstring[0] == '0':
        li = [10, 12, 13, 16, 18, 19]
        prohibited_traits += li
    if binstring[1] == '0':
        prohibited_traits.append(0)
    if binstring[2] == '0':
        li = [4, 16]
        prohibited_traits += li

    return prohibited_traits

# Divides a set on a specific column. Can handle numeric
# or nominal values
def divideset(rows,column,value):
   # Make a function that tells us if a row is in
   # the first group (true) or the second group (false)
   split_function=None
   if isinstance(value,int) or isinstance(value,float):
      split_function=lambda row: (row[column]>=value)
   else:
      split_function=lambda row: (row[column]==value)

   # Divide the rows into two sets and return them
   set1=[row for row in rows if row[column] == MISSINGCHAR or split_function(row)]
   set2=[row for row in rows if row[column] == MISSINGCHAR or not split_function(row)]
   return (set1,set2)

# Create counts of possible results (the last column of
# each row is the result, from order to species)
def uniquecounts(rows,scorevar):
   results={}
   for row in rows:
      # The result is in the column specified by scorevar
      r=row[scorevar]
      if r not in results: results[r]=0
      results[r]+=1
   print(results)
   return results  # An array of count of last unique col

# Entropy is the sum of p(x)log(p(x)) across all
# the different possible results
def entropy(rows,scorevar):
   from math import log
   log2=lambda x:log(x)/log(2)
   results=uniquecounts(rows,scorevar)
   # Now calculate the entropy
   ent=0.0
   for r in results.keys(  ):
      p=float(results[r])/len(rows)
      ent=ent-p*log2(p)
   return ent

def variance(rows):
  if len(rows)==0: return 0
  data=[float(row[len(row)-1]) for row in rows]
  mean=sum(data)/len(data)
  variance=sum([(d-mean)**2 for d in data])/len(data)
  return variance



def prune(tree,mingain):
  # If the branches aren't leaves, then prune them
  if tree.tb.results==None:
    prune(tree.tb,mingain)
  if tree.fb.results==None:
    prune(tree.fb,mingain)

  # If both the subbranches are now leaves, see if they
  # should merged
  if tree.tb.results!=None and tree.fb.results!=None:
    # Build a combined dataset
    tb,fb=[],[]
    for v,c in tree.tb.results.items(  ):
      tb+=[[v]]*c
    for v,c in tree.fb.results.items(  ):
      fb+=[[v]]*c

    # Test the reduction in entropy
    delta=entropy(tb+fb)-(entropy(tb)+entropy(fb)/2)
    if delta<mingain:
      # Merge the branches
      tree.tb,tree.fb=None,None
      tree.results=uniquecounts(tb+fb)

def classify(observation,tree):
  if tree.results!=None:
    return tree.results
  else:
    v=observation[tree.col]
    if v==None:
      tr,fr=classify(observation,tree.tb),classify(observation,tree.fb)
      tcount=sum(tr.values(  ))
      fcount=sum(fr.values(  ))
      tw=float(tcount)/(tcount+fcount)
      fw=float(fcount)/(tcount+fcount)
      result={}
      for k,v in tr.items(): result[k]=v*tw
      for k,v in fr.items(): result[k]=result.setdefault(k,0)+(v*fw)
      return result
    else:
      if isinstance(v,int) or isinstance(v,float):
        if v>=tree.value: branch=tree.tb
        else: branch=tree.fb
      else:
        if v==tree.value: branch=tree.tb
        else: branch=tree.fb
      return classify(observation,branch)

# ============ Non-binary trees

# Entropy is the sum of p(x)log(p(x)) across all
# the different possible results
def entropy1(rows,class_column):
   log2=lambda x:log(x)/log(2)
   results=uniquecounts(rows,class_column)
   # Now calculate the entropy
   ent=0.0
   for r in results.keys(  ):
      p=float(results[r])/len(rows)  # probability at the level
      ent=ent-p*log2(p)

   return ent


# Divides a set on a specific column. Can handle numeric
# or nominal values
def buildtree1(rows, scorevar, max_depth, prohibited=[],
               scoref=entropy1, min_gain=0):
  log2 = lambda x: log(x) / log(2)
  if len(rows)==0: return decisionnode(  )
  current_score=scoref(rows,scorevar)

  # Set up some variables to track the best criteria
  best_gain=0
  best_criteria=None
  best_column=None

  column_count = STOPPING_INDEX

  for col in range(0, column_count):
    if col in prohibited:  # skip the prohibited attributes
        continue
    # Generate the list of different values in
    # this column
    column_values={}
    # normal categorical attributes
    if col not in NUMERICAL + NUMBER_RANGE:
        for row in rows:  # iterate over each row
            if row[col] == MISSINGCHAR:  # skip "?"
                continue

            new_list = (str(row[col])).split(" or ")  # split by "or" in case there are multiple possible values
            for feature in list(new_list):
                newStr = feature
                column_values[newStr]=[]  # assign categorical values as keys
    #  Handle numerical attributes
    if col in NUMERICAL:
        # Divide the numerical attribute
        column_values = divideset1(rows, col, scorevar)  # pass all rows, current col_num, and total col_num

        if column_values is None:
            continue

        for key in column_values.keys():
            if key != "Less than":
                my_key = key

            my_tuple = (col, my_key)

        if my_tuple[0] in prohibited:
            column_values = None

    # Not used for this year (for attributes upper and lower bounds)
    elif col in NUMBER_RANGE:
        column_values = divideset_interval(rows, col, scorevar)

        if column_values is None:
            continue

        for key in column_values.keys():
            if key != "Not inside":
                my_key = key

            my_tuple = (col, my_key)

        if my_tuple in prohibited:
            column_values = None

    else:
        for row in rows:
            if row[col] == MISSINGCHAR:
                for value in column_values.keys():
                    column_values[value].append(row)

            elif " or " in str(row[col]):
                new_list = (str(row[col])).split(" or ")
                for feature in list(new_list):
                    newStr = feature
                    column_values[newStr].append(row)

            else:
                 column_values[row[col]].append(row)

    if column_values is None or len(column_values.keys()) < 2:
        continue

    gain = current_score
    intrinsic_info = 0
    # Gain ratio
    for key, val_rows in column_values.items():
        p = float(len(val_rows) / len(rows))
        gain -= p * scoref(val_rows, scorevar)

        intrinsic_info -= p*log2(p)
    try:
        gain = gain/intrinsic_info
    except:
        pass

    if gain > best_gain:
        best_gain = gain
        best_criteria = (col, column_values.keys())
        best_column = column_values  # choose the best col with most gain ratio

    # not allow split numerical attr multiple times (prohibited)
    if best_criteria is not None and (best_criteria[0] in NUMERICAL + NUMBER_RANGE):
        for key in best_criteria[1]:
            if key != "Less than" and key != "Not inside":
                my_key = key

        prohibited.append((best_criteria[0], my_key))

  # Create the subbranches
  if best_gain > min_gain:
    children = {}
    for key, val_rows in best_column.items():
        # Build the tree recursively
        children[key] = buildtree1(val_rows, scorevar, current_depth + 1, max_depth, prohibited, min_gain=min_gain)
    return decisionnode1(col=best_criteria[0],value=best_criteria[1],
        children=children,fname=best_criteria[0])  # return the tree with all its children

  # When there are still plant hierarchy col
  elif scorevar > STOPPING_INDEX:
      new_tree = buildtree1(rows, scorevar - 1, current_depth, max_depth, prohibited, min_gain=min_gain)
      results_cat = uniquecounts(rows, scorevar).copy()
      if new_tree.results != None:
        results_cat.update(new_tree.results)  # update the current unique counts of current col
      return decisionnode1(col=new_tree.col, value=new_tree.value,
                           children=new_tree.children,results=results_cat,fname=new_tree.fname)

  else:
    return decisionnode1(results=uniquecounts(rows,scorevar))


# Divides a set on a specific column. Handles numeric
# values
def divideset1(rows, column, scorevar, scoref=entropy1):
    log2 = lambda x: log(x) / log(2)
    best_column_values = None
    best_gain = None

    for row in rows:  # iterate over each row of table (used as a benchmark to try diff splits)
        column_values = {}

        # Assign row_val a numerical value
        row_val = None
        if isinstance(row[column], int):
            row_val = row[column]
        else:
            row_val = int(row[column].split(" or ")[0])  # choose the smallest numerical value in row_val
        # Use the value as key of the dic
        column_values[str(row_val)] = []
        column_values["Less than"] = []

        # Divide the rows into two sets
        for row2 in rows:  # iterate over all row2 for each iteration of row in rows
          # Get a list of rows with numerical values in a col
          row2s = []
          if isinstance(row2[column], int):
            row2s.append(row2)
          elif " or " in row2[column]:
            arr = row2[column].split(" or ")
            dup = list(row2)  # dup = the duplicate of the current row

            for v in arr:
                # seems changing dup at current numerical col to the last num (the largest )in arr;
                dup[column] = int(v)
            # append the revised dup row to row2s with largest possible numerical value in the row of current col
            row2s.append(dup)

            # Iterate over each row in row2s
            for r in row2s:
                if r[column] >= row_val:
                    # Append the rows with larger value at current col (in the dic)
                    column_values[str(row_val)].append(r)
                else:
                    # Append the rows with smaller value at current col (in the dic)
                    column_values["Less than"].append(r)
          else:
            print(row2[column])

        local_gain = 0
        intrinsic_info = 0
        # Gain ratio
        for key, val_rows in column_values.items():
            p = float(len(val_rows) / len(rows))
            local_gain -= p * scoref(val_rows, scorevar)

            try:
                intrinsic_info -= p * log2(p)
            except:
                pass

        try:
            local_gain = local_gain / intrinsic_info
        except:
            pass

        if best_gain is None or local_gain > best_gain:
            key = str(row_val)
            best_column_values = column_values.copy()  # choose divided set with most gain ratio

    if best_column_values is None:
        return None
    elif len(best_column_values[key]) == 0 or len(best_column_values["Less than"]) == 0:
        return None
    else:
        return best_column_values

# Gets the intervals from a list of two columns
def get_intervals(rows, column):
    value_list = []
    for row in rows:
        lower = row[column]
        upper = row[column + 1]

        if lower == MISSINGCHAR:
            lower = -1
        if upper == MISSINGCHAR:
            upper = -1

        value_list.append(lower)
        value_list.append(upper)

    sorted_list = sorted(value_list)

    interval_list = []

    for i in range(len(sorted_list) - 1):
        if sorted_list[i] == -1 or sorted_list[i+1] == sorted_list[i]:
            continue

        interval_list.append((sorted_list[i], sorted_list[i+1]))

    return interval_list

# Divides a set on two column with intervals
def divideset_interval(rows, column, scorevar, scoref=entropy1):
    log2 = lambda x: log(x) / log(2)
    interval_list = get_intervals(rows, column)
    best_column_values = None
    best_gain = None
    best_key = None

    for tuple in interval_list:
        column_values = {}
        range_key = str(tuple[0]) + "-" + str(tuple[1])
        column_values[range_key] = []
        column_values["Not inside"] = []

        # Divide the rows into two sets
        for row in rows:
            if row[column] == MISSINGCHAR or row[column+1] == MISSINGCHAR:
                column_values[range_key].append(row)
                column_values["Not inside"].append(row)
                continue

            row_tuple = (row[column], row[column+1])
            result = check_in_interval(row_tuple, tuple)

            if result == 0:
                column_values["Not inside"].append(row)
            elif result == 1:
                column_values[range_key].append(row)
                column_values["Not inside"].append(row)
            elif result == 2:
                column_values[range_key].append(row)

        local_gain = 0
        intrinsic_info = 0
        first_check = True
        # Gain ratio
        for key, val_rows in column_values.items():
            p = float(len(val_rows) / len(rows))
            if first_check:
                intrinsic_info = (-p * log2(p))
                first_check = False
            intrinsic_info -= p * log2(p)
            local_gain -= p * scoref(val_rows, scorevar)
            try:
                local_gain = local_gain / intrinsic_info
            except:
                pass
        if best_gain is None or local_gain > best_gain:
            best_key = range_key
            best_column_values = column_values.copy()

        if best_column_values is None:
            return None
        elif len(best_column_values[best_key]) == 0 or len(best_column_values["Not inside"]) == 0:
            return None
        else:
            return best_column_values

# Checks if tuple1 is inside the range of tuple2
def check_in_interval(tuple1, tuple2):
    if tuple1[0] == tuple2[0] and tuple1[1] == tuple2[1]:  # Inside interval
        return 2
    elif tuple2[0] <= tuple1[0] <= tuple2[1] or tuple2[0] <= tuple1[1] <= tuple2[1]:
        return 1
    elif tuple1[0] < tuple2[0] and tuple1[1] > tuple2[1]:
        return 1
    else:
        return 0

class decisionnode1:
  def __init__(self,col=-1,value=None,results=None,tb=None,fb=None,children=None,fname=None):
    self.col=col
    self.value=value
    self.results=results
    self.tb=tb
    self.fb=fb
    self.children = children # TBD remove if does not work
    self.fname=fname
