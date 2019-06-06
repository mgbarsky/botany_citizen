from PIL import Image, ImageDraw


def getwidth(tree):
    if tree == None: return 0
    if tree.children==None: return 1
    width = 0
    for value in tree.children.values():
        width += getwidth(value)
    return width

def getdepth(tree):
    if tree == None: return 0
    if tree.children==None: return 0
    max = 0
    for value in tree.children.values():
      candidate = 1 + getdepth(value)
      if candidate > max:
          max = candidate
    return max

def drawnode(draw,tree,x,y,feature_dict):
  if tree.children is not None:
    # Get the left and right "endpoints" of this node
    numnodes = 0
    for value in tree.children.values():
        numnodes += getwidth(value)


    left = x - numnodes*75
    right = x + numnodes*75

    dividelen = (right - left)/(len(tree.children) + 1)

    # Draw the condition string
    draw.text((x-100,y-10),"{}?".format(feature_dict[tree.col]), (0,0,0))

    # Draw the result if there is one
    if tree.results is not None:
        txt = ' \n'.join(['%s:%d' % v for v in tree.results.items()])
        draw.text((x - 20, y), txt, (0, 0, 0))

    temp = 1
    for value in tree.children.values():
        # Draw a link to the branch
        draw.line((x, y, left + temp*dividelen, y + 100), fill=(255, 0, 0))
        # Draw the branch node
        drawnode(draw, value, left + temp*dividelen, y + 100, feature_dict)
        temp += 1
  else:
    txt=' \n'.join(['%s:%d'%v for v in tree.results.items(  )])
    draw.text((x-20,y),txt,(0,0,0))

def drawtree(tree,feature_dict,jpeg='tree.jpg'):
  w=getwidth(tree)*200
  h=getdepth(tree)*100+120

  img=Image.new('RGB',(w,h),(255,255,255))
  draw=ImageDraw.Draw(img)

  drawnode(draw,tree,w/2,20,feature_dict)
  img.save(jpeg,'JPEG')
